from parcv.ResumeParser import ResumeParser
from parcv.ResumeReader import ResumeReader
from parcv.ResumeSegmenter import ResumeSegmenter
from parcv.Models import Models 
import json

class Parser:
    def __init__(self, pickle=False, load_pickled=False):
        self.models = Models()
        self.__load_models(pickle, load_pickled)
        self.reader = ResumeReader()
        self.segmenter = ResumeSegmenter(self.zero_shot_classifier)
        self.parser = ResumeParser(self.ner, self.ner_dates, self.zero_shot_classifier, self.tagger, self.qa_squad) 

    def parse(self, file_path):
        self.resume_lines = self.reader.read_file(file_path)
        self.resume_segments = self.segmenter.segment(self.resume_lines) 
        self.output = self.parser.parse(self.resume_segments)
        return self.output

    def save_as_json(self, file_name="output.json"):
        if not self.output: return 
        with open(file_name, 'w', encoding="utf-8") as f:
            json.dump(self.output, f, indent=4, default=str, ensure_ascii=False)
    
    def get_resume_lines(self):
        if self.resume_lines:
            return self.resume_lines
    
    def get_resume_segments(self):
        return self.resume_segments
    
    def __load_models(self, pickle,  load_pickled):
        self.ner, self.ner_dates, self.zero_shot_classifier, self.tagger, self.qa_squad = self.models.load_trained_models(False, load_pickled)

