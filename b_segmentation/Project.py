import logging as log
from b_segmentation.Document import Document
from typing import List
from services.segments_database import get_transformed_documents_by_project_id

class Project:
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.documents: List[Document] = []

    def get_documents(self):
        log.info('getting documents for project {0} and split into chapters'.format(self.project_id))
        for document in get_transformed_documents_by_project_id(self.project_id):
            d = Document(document[0], document[1], document[2])
            self.documents.append(d)

    def segment(self):
        for document in self.documents:
            document.create_chapters()

    def preprocess(self):
        for document in self.documents:
            document.preprocess_chapters()

    def nest_chapters(self):
        for document in self.documents:
            document.nest_chapters()

    def save(self):
        log.info('saving project {0}'.format(self.project_id))
        for d in self.documents:
            d.save()
