from parcv.Models import Models 

class ResumeSegmenter:

    def __init__(self, zero_shot_classifier):
        self.zero_shot_classifier = zero_shot_classifier

    objective = (
        'career goal',
        'objective',
        'career objective',
        'employment objective',
        'professional objective',
        'summary',
        'summary of qualifications',
    )

    work_and_employment = (
        'employment history',
        'employment data',
        'career summary',
        'work history',
        'work experience',
        'experience',
        'professional experience',
        'professional background',
        'professional employment',
        'additional experience',
        'career related experience',
        "professional employment history",
        'related experience',
        'programming experience',
        'freelance',
        'freelance experience',
        'army experience',
        'military experience',
        'military background',
    )

    education_and_training = (
        'academic background',
        'academic experience',
        'programs',
        'courses',
        'related courses',
        'education',
        'educational background',
        'educational qualifications',
        'educational training',
        'education and training',
        'training',
        'academic training',
        'professional training',
        'course project experience',
        'related course projects',
        'internship experience',
        'internships',
        'apprenticeships',
        'college activities',
        'certifications',
        'special training',
    )

    skills_header = (
        'credentials',
        'qualifications',
        'areas of experience',
        'areas of expertise',
        'areas of knowledge',
        'skills',
        "other skills",
        "other abilities",
        'digital skills',
        'career related skills',
        'professional skills',
        'specialized skills',
        'technical skills',
        'computer skills',
        'personal skills',
        'computer knowledge',        
        'technologies',
        'technical experience',
        'proficiencies',
        'languages',
        'language competencies and skills',
        'programming languages',
        'competencies'
    )

    misc = (
        'activities and honors',
        'activities',
        'affiliations',
        'professional affiliations',
        'associations',
        'professional associations',
        'memberships',
        'professional memberships',
        'athletic involvement',
        'community involvement',
        'refere',
        'civic activities',
        'extra-Curricular activities',
        'professional activities',
        'volunteer work',
        'volunteer experience',
        'additional information',
        'interests'
    )

    accomplishments = (
        'achievement',
        'awards and achievements',
        'licenses',
        'presentations',
        'conference presentations',
        'conventions',
        'dissertations',
        'exhibits',
        'papers',
        'publications',
        'professional publications',
        'research experience',
        'research grants',
        'project',
        'research projects',
        'personal projects',
        'current research interests',
        'thesis',
        'theses',
    )


    def find_segment_indices(self, string_to_search, resume_segments, resume_indices):
        for i, line in enumerate(string_to_search):

            if line[0].islower():
                continue

            header = line.lower()

            if [o for o in self.objective if header.startswith(o)]:
                try:
                    resume_segments['objective'][header]
                except:
                    resume_indices.append(i)
                    header = [o for o in self.objective if header.startswith(o)][0]
                    resume_segments['objective'][header] = i
            elif [w for w in self.work_and_employment if header.startswith(w)]:
                try:
                    resume_segments['work_and_employment'][header]
                except:
                    resume_indices.append(i)
                    header = [w for w in self.work_and_employment if header.startswith(w)][0]
                    resume_segments['work_and_employment'][header] = i
            elif [e for e in self.education_and_training if header.startswith(e)]:
                try:
                    resume_segments['education_and_training'][header]
                except:
                    resume_indices.append(i)
                    header = [e for e in self.education_and_training if header.startswith(e)][0]
                    resume_segments['education_and_training'][header] = i
            elif [s for s in self.skills_header if header.startswith(s)]:
                try:
                    resume_segments['skills'][header]
                except:
                    resume_indices.append(i)
                    header = [s for s in self.skills_header if header.startswith(s)][0]
                    resume_segments['skills'][header] = i
            elif [m for m in self.misc if header.startswith(m)]:
                try:
                    resume_segments['misc'][header]
                except:
                    resume_indices.append(i)
                    header = [m for m in self.misc if header.startswith(m)][0]
                    resume_segments['misc'][header] = i
            elif [a for a in self.accomplishments if header.startswith(a)]:
                try:
                    resume_segments['accomplishments'][header]
                except:
                    resume_indices.append(i)
                    header = [a for a in self.accomplishments if header.startswith(a)][0]
                    resume_segments['accomplishments'][header] = i

    def slice_segments(self, string_to_search, resume_segments, resume_indices):
        resume_segments['contact_info'] = string_to_search[:resume_indices[0]]
        sec_idxs = {} 
        for section, value in resume_segments.items():
            if section == 'contact_info':
                continue
            
            for sub_section, start_idx in value.items():
                end_idx = len(string_to_search)
                if (resume_indices.index(start_idx) + 1) != len(resume_indices):
                    end_idx = resume_indices[resume_indices.index(start_idx) + 1]
                
                sec_idxs[section] = (start_idx, end_idx)

                resume_segments[section][sub_section] = string_to_search[start_idx:end_idx]
        return sec_idxs

    def find_true_segment(self, dict_of_segments, segment_name):
        segment_classes = {
            'objective': ["objective", "other"],
            'work_and_employment':["employment history", "other"],
            'education_and_training': ["education and universities", "other"],
            'skills': ["skills", "other"],
            'accomplishments': ["accomplishments", "other"],
            'misc': ["misc", "other"],
            'contact_info': ["contact information", "other"]
        }
        classes = segment_classes[segment_name]
        scores = []
        segs = dict_of_segments.keys()
        for seg in segs:
            sequence = dict_of_segments[seg]
            score = self.zero_shot_classifier(' '.join(sequence), classes)["scores"][0]
            scores.append(score)
        
        res = sorted(zip(dict_of_segments.keys(), scores), key=lambda x: x[1], reverse=True)
        if len(res):
            return res[0][0]
        else: return 0 

    def segment(self, string_to_search):
        resume_segments = {
            'objective': {},
            'work_and_employment': {},
            'education_and_training': {},
            'skills': {},
            'accomplishments': {},
            'misc': {}
        }

        resume_indices = []

        self.find_segment_indices(string_to_search, resume_segments, resume_indices)
        if len(resume_indices) != 0:
            sec_idx = self.slice_segments(string_to_search, resume_segments, resume_indices)
        else:
            resume_segments['contact_info'] = []

        for segment in resume_segments:
            if segment == "contact_info": continue
            if not len(resume_segments[segment]) > 1:
                if len(resume_segments[segment]) == 1: 
                    only_key = list(resume_segments[segment].keys())[0]
                    resume_segments[segment] = resume_segments[segment][only_key][1:]
                    continue
            if segment not in ["work_and_employment", "education_and_training", "skills"]: continue
            true_seg = self.find_true_segment(resume_segments[segment], segment)
            if not true_seg: 
                resume_segments[segment] = []
            else:     
                resume_segments[segment] = resume_segments[segment][true_seg][1:]
            
        return resume_segments
