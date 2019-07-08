from services.segments_database import do_query

threshold = 0.2

query = """
    UPDATE word inner JOIN (
SELECT word, count(*) as score
from word
where tfidf > {0}
GROUP BY word
) as a ON word.word = a.word
    SET word.score = a.score
    """.format(threshold)

do_query(query)
