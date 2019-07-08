from services.segments_database import do_query

query = """
TRUNCATE TABLE word;
TRUNCATE TABLE chapter;
UPDATE document SET status = 'CONVERTED' WHERE status = 'CHAPTERS_EXTRACTED';
"""

do_query(query)