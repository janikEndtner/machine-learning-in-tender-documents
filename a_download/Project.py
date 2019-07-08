import logging as log
import requests
from services.segments_database import insert_document, insert_project
from sqlalchemy.exc import OperationalError, IntegrityError
from helpers.Status import Status
from requests.exceptions import HTTPError
import traceback
from segments_database import do_query

class Project:

    def __init__(self, project_id):
        self.project_id = project_id
        self.files = []

    def get_files_from_es(self, es_request, words):
        log.info('Create ES requrest for project {0}'.format(self.project_id))

        url = 'http://elasticapitest.digisus.ch/bodysearch'.format(self.project_id)
        body = es_request \
            .replace("%%PROJECT_NUMBER%%", str(self.project_id)) \
            .replace("%%QUERY%%", " ".join(words))
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=body)

        found = False
        if len(r.json()) > 1:
            for f in r.json()[1:]:
                try:
                    if f['ES']['_source']['file'] and f['ES']['_source']['file']['extension'] not in ['zip', '7z', 'rar']:
                        found = True
                        self.files.append({
                            'file_browser': f['fs']['file_browser'],
                            'file_download': f['fs']['file_download'],
                            'filename': f['ES']['_source']['file']['filename'],
                            'extension': f['ES']['_source']['file']['extension']
                        })
                    else:
                        log.info('zip file found. skipping')
                except KeyError:
                    log.error('ES response had bad structure')

        if not found:
            log.warning('NO FILES FOUND FOR PROJECT {0}'.format(self.project_id))

    def download_and_save_files(self):
        try:
            insert_project(self.project_id)
        except IntegrityError:
            print('this project is already downloaded')
            pass

        for f in self.files:

            # check if file exists already
            query = 'select * from document where project_id = {0} and document_name = "{1}"'\
                .format(self.project_id, f['filename'])
            if len(do_query(query).fetchall()) > 0:
                print('document {0} for project {1} exists already'.format(self.project_id, f['filename']))
                continue

            log.info('Writing file {0}'.format(f['filename']))
            try:
                response = requests.get(f['file_download'], stream=True)
                response.raise_for_status()

                insert_document(f['filename'], f['file_download'], f['file_browser'], response.content, self.project_id,
                                f['extension'])
            except OperationalError:
                traceback.print_exc()
                log.warning('PDF is too big to save')
                insert_document(f['filename'], f['file_download'], f['file_browser'], None, self.project_id,
                                f['extension'], status=Status.PDF_TOO_BIG)
            except HTTPError:
                log.warning('HTTP error')
                insert_document(f['filename'], f['file_download'], f['file_browser'], None, self.project_id,
                                f['extension'], status=Status.HTTP_ERROR)
