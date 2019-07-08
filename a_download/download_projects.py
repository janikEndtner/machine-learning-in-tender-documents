import configparser
import logging as log
import sys
from services import simap_database
import random
from a_download.Project import Project
import time

# CONFIG

WORDS = [
    "Eignungskriteri*",
    "Zuschlagskriteri*",
    "Zulassungskri*"
]

ES_REQUEST = """
    {
        "index": "simap_minio_copy",
        "body": {
          "query": {
            "bool": {
              "must": {
                "query_string": {
                  "default_field": "content",
                  "query": "%%QUERY%%",
                  "default_operator": "OR"
                }
              },
              "should": [
                        {
                          "term": {
                            "project_number": %%PROJECT_NUMBER%%
                          }
                        }
              ],
              "minimum_should_match": "1"
            }
          }
        },
        "from": 0,
        "size": 5
    }
"""

config = configparser.ConfigParser()
config.read('config.ini')

if config["General"]["log_level"] == 'VERBOSE':
    log.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Verbose output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s")


# RUN

def run():
    time_between_requests = int(config['General']['time_between_requests'])

    projects = simap_database.get_downloaded_projects()
    # log.info('select randomly {0} of these projects'.format(number_of_projects))
    # projects = random.sample(projects, number_of_projects)

    count = 0
    for p in projects:
        project = Project(p)
        project.get_files_from_es(ES_REQUEST, WORDS)
        project.download_and_save_files()

        count += 1
        log.info('Downloaded {0} projects of {1}'.format(count, len(projects)))
        time.sleep(time_between_requests)


run()
