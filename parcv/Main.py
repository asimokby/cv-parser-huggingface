from ResumeReader import ResumeReader
from ResumeParser import ResumeParser
from Models import Models
import json
import os


class Main:
    def __init__(self):
        self.reader = ResumeReader()
        self.parser = ResumeParser() 

    def parse_cv(self, file_path, file_out):
        resume_lines = self.reader.read_file(file_path)
        output = self.parser.parse(resume_lines)
        self.save_parse_as_json(output, file_out)
        
    def save_parse_as_json(self, dict, file_name):
        print("Saving the parse...")
        with open(file_name, 'w', encoding="utf-8") as f:
            json.dump(dict, f, indent=4, default=str, ensure_ascii=False)
    
    def load_trained_models(self):
        models = Models()
        models.load_trained_models(pickle=True)
    

main = Main()
parent_dir = "cvs"
files = os.listdir(parent_dir)
for filename in files:
    print(f"##### Processing: {filename} #####")
    source_filename = f"{parent_dir}/{filename}"
    target_out = f"parsed_cvs/{filename.split('.')[0]}.json"
    main.parse_cv(source_filename, target_out)
    
