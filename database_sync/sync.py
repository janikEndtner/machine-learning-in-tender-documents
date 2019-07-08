import configparser
import sys
from time import sleep
from services.segments_database import get_documents_by_status, update_status, update_content_transformed
from os import listdir, remove, rename
from os.path import isfile, join, exists
from helpers.Status import Status
from sqlalchemy.exc import OperationalError

config = configparser.ConfigParser()
config.read('config.ini')

def do_sync():
    # copy files to pdf location
    print('Getting documents to convert')
    documents = get_documents_by_status(Status.READY_TO_CONVERT)

    for row in documents:
        # add random int to end of file. we need this later for renaming files
        filename = '{0}{1}_{2}.pdf'.format(config['Folders']['pdf'], row[0], row[1])
        file = open(filename, 'wb')
        print('writing file {0}'.format(filename))
        file.write(row[2])
        file.close()

        update_status(row[0], Status.CONVERTING)

    # save files from docx folder in database
    path = config['Folders']['docx']
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for filename in files:
        file = None
        file_path = ''
        try:
            document_id = int(filename.split('_')[0])
            file_path = join(path, filename)
            print("Saving converted file {0} in database".format(file_path))
            file = open(file_path, 'rb')

            try:
                update_content_transformed(document_id, file.read())
                update_status(document_id, Status.CONVERTED)
            except OperationalError:
                update_status(document_id, Status.DOCX_TOO_BIG)

        except:
            print("Unexpected error:" + sys.exc_info()[0])

        finally:
            if file is not None:
                file.close()
            if len(file_path) > 0 and exists(file_path):
                remove(file_path)
                
    # check if there is some stuff in error folder
    path = config['Folders']['error']
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for filename in files:
        document_id = int(filename.split('_')[0])
        file_path = join(path, filename)
        print('found file in error folder {0}'.format(file_path))
        update_status(document_id, Status.ERROR_WHILE_CONVERTING)
        if exists(file_path):
            remove(file_path)


    # sleep ten seconds
    sleep(60)
    do_sync()

do_sync()