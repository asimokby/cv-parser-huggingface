from transformers import AutoModelForQuestionAnswering, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from transformers import pipeline
from flair.data import Sentence
from flair.models import SequenceTagger
import pickle



class Models:

    def pickle_it(self, obj, file_name):
        with open(f'{file_name}.pickle', 'wb') as f:
            pickle.dump(obj, f)

    def unpickle_it(self, file_name):
        with open(f'{file_name}.pickle', 'rb') as f:
            return pickle.load(f)

    def load_trained_models(self, pickle=False, load_pickled=False):

        if load_pickled:
            return self.load_pickled_models()

        #NER (dates)
        tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
        model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
        self.ner_dates = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

        #Zero Shot Classification
        self.zero_shot_classifier = pipeline("zero-shot-classification", model='facebook/bart-large-mnli')
        # self.zero_shot_classifier = pipeline("zero-shot-classification", model='valhalla/distilbart-mnli-12-6')

        # Ner
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.ner = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)

        # Pos Tagging
        self.tagger = SequenceTagger.load("flair/pos-english")

        # QA
        tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
        model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
        self.qa_squad = pipeline('question-answering', model=model, tokenizer=tokenizer)

        if pickle:
            self.pickle_models()
        
        return self.ner, self.ner_dates, self.zero_shot_classifier, self.tagger, self.qa_squad



    
    def pickle_models(self):
        self.pickle_it(self.ner, "ner")
        self.pickle_it(self.zero_shot_classifier, "zero_shot_classifier")
        self.pickle_it(self.ner_dates, "ner_dates")
        self.pickle_it(self.tagger, "pos_tagger")
        self.pickle_it(self.qa_squad, "qa_squad")


    def load_pickled_models(self):
        try:
            ner_dates = self.unpickle_it('ner_dates')
            ner = self.unpickle_it('ner')
            zero_shot_classifier = self.unpickle_it('zero_shot_classifier_6')
            tagger = self.unpickle_it("pos_tagger")
            qa_squad = self.unpickle_it('qa_squad')
        except: 
            self.load_trained_models(pickle=True, load_pickled=False)
        return ner, ner_dates, zero_shot_classifier, tagger, qa_squad
    
    def get_flair_sentence(self, sent):
        return Sentence(sent)