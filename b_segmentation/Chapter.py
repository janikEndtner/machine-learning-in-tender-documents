from typing import List
from b_segmentation.GermanTextPreprocessor.GermanTextPreprocessor import GermanTextPreprocessor, UselessPreprocessor
import configparser
from services.segments_database import insert_chapter, insert_word
import logging as log
from pandas import Series

config = configparser.ConfigParser()
config.read('config.ini')

# it's possible to disable preprocessing for development because of speed
preprocess = config['General']['preprocess'] == 'True'

if preprocess:
    preprocessor = GermanTextPreprocessor()
else:
    preprocessor = UselessPreprocessor()


class Chapter:
    def __init__(self, project_id: int, document_id: int, heading_number: str, heading_title: str, content: str, level: int):
        self.project_id = project_id
        self.document_id = document_id
        self.heading_number = heading_number
        self.heading_title = heading_title
        self.heading_preprocessed: str = ''
        self.content = content
        self.level = level
        self.preprocessed_content: List[str] = []
        self.parent: str = ''
        self.parent_preprocessed = ''
        self.grand_parent: str = ''
        self.grand_parent_preprocessed = ''
        self.tf_idf_scores: Series = []

    def merge_with_string(self, to_merge: str):
        self.content += '\n{0}'.format(to_merge)

    def merge_with_chapter(self, chapter: 'Chapter'):
        self.content += '\n{0} {1}'.format(chapter.heading_number, chapter.content)
        self.preprocessed_content += chapter.preprocessed_content

    def preprocess_header(self):
        self.heading_preprocessed = preprocessor.preprocess_text(self.heading_title)

    def preprocess_content(self):
        self.preprocessed_content = preprocessor.preprocess_text(self.content)

    def set_parent(self, parent_title: str, parent_preprocessed: str):
        self.parent = parent_title
        self.parent_preprocessed = parent_preprocessed

    def set_grand_parent(self, grand_parent_title: str, grand_parent_preprocessed: str):
        self.grand_parent = grand_parent_title
        self.grand_parent_preprocessed = grand_parent_preprocessed

    def set_tf_idf_scores(self, tf_idf_scores: Series):
        self.tf_idf_scores = tf_idf_scores

    # chapter_idx: clear order index of chapters. first chapter has idx 0, second has idx 1, ...
    def save(self, chapter_idx: int):
        inserted = insert_chapter(
            self.content,
            self.heading_number,
            chapter_idx,
            self.heading_title,
            ' '.join(self.heading_preprocessed),
            self.parent,
            ' '.join(self.parent_preprocessed),
            self.grand_parent,
            ' '.join(self.grand_parent_preprocessed),
            self.document_id
        )
        log.debug('saving words for chapter {0}'.format(self.heading_number))
        min_tf_idf_score = float(config['General']['min_tf_idf_score'])
        for word, score in self.tf_idf_scores.iteritems():
            if score >= min_tf_idf_score and len(word) > 0:
                insert_word(word, score, inserted.lastrowid)
