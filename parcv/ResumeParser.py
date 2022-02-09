from parcv.Models import Models
from datetime import datetime
from dateutil import parser
import re
from string import punctuation
from collections import Counter

class ResumeParser:

    def __init__(self, ner, ner_dates, zero_shot_classifier, tagger):
        self.models = Models()
        self.ner, self.ner_dates, self.zero_shot_classifier, self.tagger = ner, ner_dates, zero_shot_classifier, tagger
        self.parsed_cv = {}

    def parse(self, resume_segments):
        for segment_name in resume_segments:
            if segment_name == "contact_info":
                contact_info = resume_segments[segment_name]
                self.parse_contact_info(contact_info)
            elif segment_name == "work_and_employment":
                resume_segment = resume_segments[segment_name]
                self.parse_job_history(resume_segment)
        return self.parsed_cv


    def parse_contact_info(self, contact_info):
        contact_info_dict = {}
        name = self.find_person_name(contact_info)
        email = self.find_contact_email(contact_info)
        self.parsed_cv['Name'] = name
        contact_info_dict["Email"] = email
        self.parsed_cv['Contact Info'] = contact_info_dict

    def find_person_name(self, items):
        class_score = []
        splitter = re.compile(r'[{}]+'.format(re.escape(punctuation.replace("&", "") )))
        classes = ["person name", "address", "email", "title"]
        for item in items: 
            elements = splitter.split(item)
            for element in elements:
                element = ''.join(i for i in element.strip() if not i.isdigit())
                if not len(element.strip().split()) > 1: continue
                out = self.zero_shot_classifier(element, classes)
                highest = sorted(zip(out["labels"], out["scores"]), key=lambda x: x[1])[-1]
                if highest[0] == "person name":
                    class_score.append((element, highest[1]))
        if len(class_score):
            return sorted(class_score, key=lambda x: x[1], reverse=True)[0][0]
        return ""
    
    def find_contact_email(self, items):
        for item in items: 
            match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', item)
            if match:
                return match.group(0)
        return ""

    def parse_job_history(self, resume_segment):
        idx_job_title = self.get_job_titles(resume_segment)
        current_and_below = False
        if not len(idx_job_title): 
            self.parsed_cv["Job History"] = [] 
            return
        if idx_job_title[0][0] == 0: current_and_below = True
        job_history = []
        for ls_idx, (idx, job_title) in enumerate(idx_job_title): 
            job_info = {}
            job_info["Job Title"] = self.filter_job_title(job_title) 
            # company 
            if current_and_below: line1, line2 = idx, idx+1
            else: line1, line2 = idx, idx-1 
            job_info["Company"] = self.get_job_company(line1, line2, resume_segment)
            if current_and_below: st_span = idx
            else: st_span = idx-1
            # Dates 
            if ls_idx == len(idx_job_title) - 1: end_span = len(resume_segment) 
            else: end_span = idx_job_title[ls_idx+1][0]
            start, end = self.get_job_dates(st_span, end_span, resume_segment)
            job_info["Start Date"] = start
            job_info["End Date"] = end
            job_history.append(job_info)
        self.parsed_cv["Job History"] = job_history 

    def get_job_titles(self, resume_segment):
        classes = ["organization", "institution", "company", "job title", "work details"]
        idx_line = []
        for idx, line in enumerate(resume_segment):
            has_verb = False
            line_modifed = ''.join(i for i in line if not i.isdigit())
            sentence = self.models.get_flair_sentence(line_modifed)
            self.tagger.predict(sentence)
            tags = []
            for entity in sentence.get_spans('pos'):
                tags.append(entity.tag)
                if entity.tag.startswith("V"): 
                    has_verb = True

            most_common_tag = max(set(tags), key=tags.count)
            if most_common_tag == "NNP":
                if not has_verb:
                    out = self.zero_shot_classifier(line, classes)
                    class_score = zip(out["labels"], out["scores"])
                    highest = sorted(class_score, key=lambda x: x[1])[-1]

                    if highest[0] == "job title":
                        idx_line.append((idx, line))

        return idx_line
    

    def get_job_dates(self, st, end, resume_segment):
        search_span = resume_segment[st:end]
        dates = []
        for line in search_span:
            for dt in self.get_ner_in_line(line, "DATE"):
                if self.isvalidyear(dt.strip()):
                    dates.append(dt)
        if len(dates): first = dates[0]
        exists_second = False
        if len(dates) > 1:
            exists_second = True
            second = dates[1]
        
        if len(dates) > 0:
            if self.has_two_dates(first):
                d1, d2 = self.get_two_dates(first)
                return self.format_date(d1), self.format_date(d2)
            elif exists_second and self.has_two_dates(second): 
                d1, d2 = self.get_two_dates(second)
                return self.format_date(d1), self.format_date(d2)
            else: 
                if exists_second: 
                    st = self.format_date(first)
                    end = self.format_date(second)
                    return st, end
                else: 
                    return (self.format_date(first), "") 
        else: return ("", "")

    
    
    def filter_job_title(self, job_title):
        job_title_splitter = re.compile(r'[{}]+'.format(re.escape(punctuation.replace("&", "") )))
        job_title = ''.join(i for i in job_title if not i.isdigit())
        tokens = job_title_splitter.split(job_title)
        tokens = [''.join([i for i in tok.strip() if (i.isalpha() or i.strip()=="")]) for tok in tokens if tok.strip()] 
        classes = ["company", "organization", "institution", "job title", "responsibility",  "details"]
        new_title = []
        for token in tokens:
            if not token: continue
            res = self.zero_shot_classifier(token, classes)
            class_score = zip(res["labels"], res["scores"])
            highest = sorted(class_score, key=lambda x: x[1])[-1]
            if highest[0] == "job title":
                new_title.append(token.strip())
        if len(new_title):
            return ', '.join(new_title)
        else: return ', '.join(tokens)

    def has_two_dates(self, date):
        years = self.get_valid_years()
        count = 0
        for year in years:
            if year in str(date):
                count+=1
        return count == 2
    
    def get_two_dates(self, date):
        years = self.get_valid_years()
        idxs = []
        for year in years:
            if year in date: 
                idxs.append(date.index(year))
        min_idx = min(idxs)  
        first = date[:min_idx+4]
        second = date[min_idx+4:]
        return first, second
    def get_valid_years(self):
        current_year = datetime.today().year
        years = [str(i) for i in range(current_year-100, current_year)]
        return years

    def format_date(self, date):
        out = self.parse_date(date)
        if out: 
            return out
        else: 
            date = self.clean_date(date)
            out = self.parse_date(date)
            if out: 
                return out
            else: 
                return date

    def clean_date(self, date): 
        try:
            date = ''.join(i for i in date if i.isalnum() or i =='-' or i == '/')
            return date
        except:
            return date

    def parse_date(self, date):
        try:
            date = parser.parse(date)
            return date.strftime("%m-%Y")
        except: 
            try:
                date = datetime(date)
                return date.strftime("%m-%Y")
            except: 
                return 0 


    def isvalidyear(self, date):
        current_year = datetime.today().year
        years = [str(i) for i in range(current_year-100, current_year)]
        for year in years:
            if year in str(date):
                return True 
        return False

    def get_ner_in_line(self, line, entity_type):
        if entity_type == "DATE": ner = self.ner_dates
        else: ner = self.ner
        return [i['word'] for i in ner(line) if i['entity_group'] == entity_type]
        

    def get_job_company(self, idx, idx1, resume_segment):
        job_title = resume_segment[idx]
        if not idx1 <= len(resume_segment)-1: context = ""
        else:context = resume_segment[idx1]
        candidate_companies = self.get_ner_in_line(job_title, "ORG") + self.get_ner_in_line(context, "ORG")
        classes = ["organization", "company", "institution", "not organization", "not company", "not institution"]
        scores = []
        for comp in candidate_companies:
            res = self.zero_shot_classifier(comp, classes)['scores']
            scores.append(max(res[:3]))
        sorted_cmps = sorted(zip(candidate_companies, scores), key=lambda x: x[1], reverse=True)
        if len(sorted_cmps): return sorted_cmps[0][0]
        return context