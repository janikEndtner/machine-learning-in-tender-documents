from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

from b_segmentation.Chapter import Chapter
from docx import Document as DocxDocument
from b_segmentation.segment_helpers import iter_block_items
import re
import pandas as pd
import logging as log
import io
from services.segments_database import update_status
from helpers.Status import Status

class Document:
    def __init__(self, document_id: int, project_id: int, docx_file: bytes):
        self.document_id = document_id
        self.project_id = project_id
        self.docx_file = docx_file
        self.chapters: List[Chapter] = []

    def create_chapters(self) -> List[Chapter]:
        docx = DocxDocument(io.BytesIO(self.docx_file))
        p = re.compile("^[\s\n]*$")

        current_numbering = {
            'first_level': 0,
            'second_level': 0,
            'third_level': 0
        }

        for block in iter_block_items(docx):
            if block.is_header() or len(self.chapters) == 0:
                heading_numb = None
                level = 0
                if 'Heading 1' in block.get_element_style_name():
                    current_numbering['first_level'] += 1
                    current_numbering['second_level'] = 0
                    current_numbering['third_level'] = 0
                    heading_numb = current_numbering['first_level']
                    level = 1
                elif 'Heading 2' in block.get_element_style_name():
                    current_numbering['second_level'] += 1
                    current_numbering['third_level'] = 0
                    heading_numb = '{0}.{1}'.format(current_numbering['first_level'], current_numbering['second_level'])
                    level = 2
                elif 'Heading 3' in block.get_element_style_name():
                    current_numbering['third_level'] += 1
                    heading_numb = '{0}.{1}.{2}'.format(current_numbering['first_level'],
                                                        current_numbering['second_level'],
                                                        current_numbering['third_level'])
                    level = 3

                block_str = block.to_string()
                self.chapters.append(
                    Chapter(self.project_id, self.document_id, heading_numb, block_str, '', level)
                )

            else:
                # append only if it's not empty
                if re.match(p, block.to_string()) is None:
                    self.chapters[-1].merge_with_string(block.to_string())

        return self.chapters

    def preprocess_chapters(self):
        for chapter in self.chapters:
            log.debug('preprocessing {0} {1}'.format(chapter.heading_number, chapter.heading_title.replace('\n', '')))
            chapter.preprocess_header()
            chapter.preprocess_content()
        self.calculate_tf_idf()

    def calculate_tf_idf(self):
        log.info('calculating tf idf scores')

        corpus = list(map(lambda x: '<space>'.join(x.preprocessed_content), self.chapters))

        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split("<space>"))

        df = pd.DataFrame(vectorizer.fit_transform(corpus).toarray())
        df.columns = vectorizer.get_feature_names()

        for i in range(0, len(df)):
            features = df.loc[i, df.loc[i] > 0]
            self.chapters[i].set_tf_idf_scores(features)

    def nest_chapters(self):
        for i, chapter in enumerate(self.chapters):
            current_level = chapter.level
            j = i + 1
            while j < len(self.chapters) and self.chapters[j].level > current_level > 0:
                # add chapter text to parent
                chapter.merge_with_chapter(self.chapters[j])
                # add headers to children
                if self.chapters[j].level - current_level == 1:
                    self.chapters[j].set_parent(chapter.heading_title, chapter.heading_preprocessed)
                elif self.chapters[j].level - current_level == 2:
                    self.chapters[j].set_grand_parent(chapter.heading_title, chapter.heading_preprocessed)
                else:
                    raise ValueError('Something is wrong here...')
                j += 1

    def save(self):
        update_status(self.document_id, Status.CHAPTERS_EXTRACTED)
        for i, chapter in enumerate(self.chapters):
            chapter.save(i)
