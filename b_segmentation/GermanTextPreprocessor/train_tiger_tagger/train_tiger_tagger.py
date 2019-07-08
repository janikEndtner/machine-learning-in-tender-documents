import nltk
import pickle
import random
from b_segmentation.GermanTextPreprocessor.ClassifierBasedGermanTagger.ClassifierBasedGermanTagger import ClassifierBasedGermanTagger


# see code https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

corp = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09',
                                     ['ignore', 'words', 'ignore', 'ignore', 'pos'],
                                     encoding='utf-8')

tagged_sents = [sentence for sentence in corp.tagged_sents()]
random.shuffle(tagged_sents)

# set a split size: use 90% for training, 10% for testing
split_perc = 0.1
split_size = int(len(tagged_sents) * split_perc)
train_sents, test_sents = tagged_sents[split_size:], tagged_sents[:split_size]

tagger = ClassifierBasedGermanTagger(train=train_sents)

# print(tagger.tag(['Das', 'ist', 'ein', 'einfacher', 'Test']))
# accuracy = tagger.evaluate(test_sents)
# print(accuracy)

with open('nltk_german_classifier_data.pickle', 'wb') as f:
    pickle.dump(tagger, f, protocol=2)
