from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from transformers import pipeline
from flair.data import Sentence
from flair.models import SequenceTagger
import pickle



class Models:

    def pickle_it(self, obj, file_name):
        with open(f'pickled_models/{file_name}.pickle', 'wb') as f:
            pickle.dump(obj, f)

    def unpickle_it(self, file_name):
        with open(f'pickled_models/{file_name}.pickle', 'rb') as f:
            return pickle.load(f)

    def load_trained_models(self, pickle=True):
        #NER (dates)
        tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
        model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
        self.ner_dates = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

        #Zero Shot Classification
        # self.zero_shot_classifier = pipeline("zero-shot-classification", model='facebook/bart-large-mnli')
        self.zero_shot_classifier = pipeline("zero-shot-classification", model='valhalla/distilbart-mnli-12-6')

        # Ner
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.ner = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)

        # Pos Tagging
        self.tagger = SequenceTagger.load("flair/pos-english-fast")

        if pickle:
            self.pickle_models()
    
    def pickle_models(self):
        self.pickle_it(self.ner, "ner")
        self.pickle_it(self.zero_shot_classifier, "zero_shot_classifier_6")
        self.pickle_it(self.ner_dates, "ner_dates")
        self.pickle_it(self.tagger, "pos_tagger_fast")


    def load_pickled_models(self):
        ner_dates = self.unpickle_it('ner_dates')
        ner = self.unpickle_it('ner')
        zero_shot_classifier = self.unpickle_it('zero_shot_classifier_6')
        tagger = self.unpickle_it("pos_tagger_fast")
        return ner_dates, ner, zero_shot_classifier, tagger
    
    def get_flair_sentence(self, sent):
        return Sentence(sent)