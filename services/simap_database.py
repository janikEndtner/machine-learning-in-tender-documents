import configparser
import logging as log
import pandas as pd
from sqlalchemy.dialects import mysql

config = configparser.ConfigParser()


def create_connection():
    config.read('../config.ini')
    db = mysql.connector.connect(
        user=config['DB']['user'],
        password=config['DB']['password'],
        host=config['DB']['host'],
        database=config['DB']['database']
    )
    return db


# def get_downloaded_projects():
#     db = create_connection()
#     log.info("Getting downloaded projects")
#     query = ("""SELECT DISTINCT projekt_id
#              FROM projekt
#              INNER JOIN ausschreibung USING (projekt_id)
#              WHERE sprache = 'DE'
#              AND projekt.unterlagen_heruntergeladen = 'ja'
#              ORDER BY datum_publikation DESC""")
#     cursor = db.cursor(buffered=True)
#     cursor.execute(query)
#     result = list(cursor)
#     db.close()
#     log.info("Found %d projects" % len(result))
#     return result

def get_downloaded_projects():
    result = pd.read_csv('db_helpers/projekt.csv')
    log.info("Found %d projects" % len(result))
    result = result['project_id'].tolist()
    return result
