import sys
from b_segmentation.Project import Project
import configparser
import logging as log
from services.segments_database import get_documents_by_status
from helpers.Status import Status
import multiprocessing


def worker(process_id: int, project_id: int, project_length):
    config = configparser.ConfigParser()
    config.read('config.ini')

    if config["General"]["log_level"] == 'VERBOSE':
        log.basicConfig(stream=sys.stdout,
                        format="Pool {0}: %(pathname)s:%(lineno)d %(levelname)s: %(message)s".format(process_id),
                        level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="Pool {0}: %(levelname)s: %(message)s".format(process_id))
    log.info('STARTING PROCESS {0} of {1}'.format(process_id, project_length))

    project = Project(project_id)
    project.get_documents()
    project.segment()
    project.preprocess()
    project.nest_chapters()
    project.save()


def run():
    project_id_list = set(map(lambda row: row[1], get_documents_by_status(Status.CONVERTED)))
    counter = 0

    for projectId in project_id_list:
        counter += 1
        log.info('STARTING TO PREPROCESS PROJECT {0}. ({1}/{2})'.format(projectId, counter, len(project_id_list)))
        project = Project(projectId)
        project.get_documents()
        project.segment()
        project.preprocess()
        project.nest_chapters()
        project.save()


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')

    if config["General"]["log_level"] == 'VERBOSE':
        log.basicConfig(stream=sys.stdout, format="%(pathname)s:%(lineno)d %(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    project_id_list = set(map(lambda row: row[1], get_documents_by_status(Status.CONVERTED)))

    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1 or 1)

    for idx, project_id in enumerate(project_id_list):
        pool.apply_async(worker, args=(idx, project_id, len(project_id_list)))
    pool.close()
    pool.join()
