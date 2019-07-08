from nltk.corpus import stopwords
import pickle
from b_segmentation.GermanTextPreprocessor.germalemma.germalemma import GermaLemma
from nltk.tokenize import RegexpTokenizer
import os
from typing import List

pickle_path = os.getcwd() + "/b_segmentation/GermanTextPreprocessor/train_tiger_tagger/nltk_german_classifier_data.pickle"
tiger_path = os.getcwd() + "/b_segmentation/GermanTextPreprocessor/train_tiger_tagger/tiger_release_aug07.corrected.16012013.conll09"


class GermanTextPreprocessor:

    def __init__(self):
        print('initializing germantextpreprocessor...')
        self.stop_words = set(stopwords.words('german'))

        # load predefined pos tagger
        with open(pickle_path, 'rb') as f:
            self.tagger = pickle.load(f)

        # load lemmatizer
        self.lemmatizer = GermaLemma(tiger_corpus=tiger_path)

        self.tokenizer = RegexpTokenizer(r'\w+')

    def tokenize(self, sentence):
        return self.tokenizer.tokenize(sentence)

    def remove_stopwords(self, words):
        words_filtered = []

        for w in words:
            if w not in self.stop_words:
                words_filtered.append(w)

        return words_filtered

    def lowercase(self, words):
        return list(map(lambda x: x.lower(), words))

    def pos_tagging(self, words):
        return self.tagger.tag(words)

    def lemmatisation(self, words):
        lemmas = []
        for w in words:
            try:
                lemma = self.lemmatizer.find_lemma(w[0], w[1])
            except ValueError:
                lemma = w[0]
            # in this case, no pos tag was found and w is still a string. just return this string
            except IndexError:
                lemma = w
            lemmas.append(lemma)

        return lemmas

    def get_tagger(self):
        return self.tagger

    def tokenize_remove_stopwords_lemma(self, list_of_sentences):

        print('tokenizing...')
        tokenized = list(map(lambda x: self.tokenize(x), list_of_sentences))

        tagged = []
        for index, word in enumerate(tokenized):
            if index % 250 == 0:
                print("POS tagging: %d done" % index)
            tagged.append(self.pos_tagging(word))

        lemmas = []
        for index, word in enumerate(tagged):
            if index % 250 == 0:
                print("Lemmatisation: %d done" % index)
            lemmas.append(self.lemmatisation(word))

        print('Making lowercase...')
        lowercase = list(map(lambda x: self.lowercase(x), lemmas))
        print('removing stop words...')
        removed_stopwords = list(map(lambda x: self.remove_stopwords(x), lowercase))

        return removed_stopwords

    def preprocess_text(self, text: str) -> List[str]:
        tokenized = self.tokenize(text)
        # print(tokenized)
        tagged = self.pos_tagging(tokenized)
        # print(tagged)
        lemmas = self.lemmatisation(tagged)
        # print(lemmas)
        lowercase = self.lowercase(lemmas)
        # print(lowercase)
        removed_stopwords = self.remove_stopwords(lowercase)
        # print(removed_stopwords)
        return removed_stopwords


class UselessPreprocessor:
    def __init__(self):
        print('processing disabled. initializing useless preprocessor')

    def preprocess_text(self, text: str) -> List[str]:
        return text.split(' ')
