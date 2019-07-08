from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, Text, DateTime, \
    ForeignKeyConstraint, \
    LargeBinary, Boolean
from helpers.Status import Status
import datetime

engine = create_engine('mysql://root:@localhost:3306/simap-segments?charset=utf8', pool_pre_ping=True)
meta = MetaData()

project = Table(
    'project', meta,
    Column('project_id', Integer, primary_key=True, autoincrement=False)
)

document = Table(
    'document', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('document_name', String(250), nullable=False),
    Column('download_link', String(250), nullable=False),
    Column('view_link', String(250), nullable=False),
    Column('content_original', LargeBinary(length=(2 ** 32) - 1), nullable=True),
    Column('content_transformed', LargeBinary(length=(2 ** 32) - 1), nullable=True),
    Column('status', String(100), unique=False, default='No'),
    Column('project_id', Integer, nullable=False),
    ForeignKeyConstraint(
        ['project_id'], ['project.project_id'],
        name='fk_project'
    )
)

chapter = Table(
    'chapter', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('text', Text, nullable=False),
    Column('chapter_idx', Integer, nullable=False),
    Column('chapter_number', String(10), nullable=True),
    Column('header', String(250), nullable=True),
    Column('header_preprocessed', String(250), nullable=True),
    Column('parent_header', String(250), nullable=True),
    Column('parent_preprocessed', String(250), nullable=True),
    Column('grandparent_header', String(250), nullable=True),
    Column('grandparent_preprocessed', String(250), nullable=True),
    Column('topic_1_id', Integer, nullable=True),
    Column('topic_1_value', Float, nullable=True),
    Column('topic_2_id', Integer, nullable=True),
    Column('topic_2_value', Float, nullable=True),
    Column('topic_3_id', Integer, nullable=True),
    Column('topic_3_value', Float, nullable=True),
    Column('topic_4_id', Integer, nullable=True),
    Column('topic_4_value', Float, nullable=True),
    Column('topic_5_id', Integer, nullable=True),
    Column('topic_5_value', Float, nullable=True),
    Column('document_id', Integer),
    ForeignKeyConstraint(
        ['document_id'], ['document.id'],
        name='fk_chapter_document'
    ),
),

word = Table(
    'word', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('word', String(100), nullable=False),
    Column('tfidf', Float, nullable=False),
    Column('score', Integer, nullable=True),
    Column('chapter_id', Integer),
    ForeignKeyConstraint(
        ['chapter_id'], ['chapter.id'],
        name='fk_word_chapter'
    )
),

trainingdata = Table(
    'trainingdata', meta,
    Column('id', Integer, primary_key=True),
    Column('text', Text, nullable=False),
    Column('chapter_idx', Integer, nullable=False),
    Column('chapter_number', String(10), nullable=True),
    Column('header', String(250), nullable=True),
    Column('header_preprocessed', String(250), nullable=True),
    Column('parent_header', String(250), nullable=True),
    Column('parent_preprocessed', String(250), nullable=True),
    Column('grandparent_header', String(250), nullable=True),
    Column('grandparent_preprocessed', String(250), nullable=True),
    Column('topic_1_id', Integer, nullable=True),
    Column('topic_1_value', Float, nullable=True),
    Column('topic_2_id', Integer, nullable=True),
    Column('topic_2_value', Float, nullable=True),
    Column('topic_3_id', Integer, nullable=True),
    Column('topic_3_value', Float, nullable=True),
    Column('topic_4_id', Integer, nullable=True),
    Column('topic_4_value', Float, nullable=True),
    Column('topic_5_id', Integer, nullable=True),
    Column('topic_5_value', Float, nullable=True),
    Column('document_id', Integer),
    Column('label', Boolean),
    Column('category', String(10)),
    Column('round', Integer),
    Column('suggested_label', Boolean),
    Column('updatedAt', DateTime, default=datetime.datetime.utcnow),
    Column('createdAt', DateTime, default=datetime.datetime.utcnow),
    ForeignKeyConstraint(
        ['document_id'], ['document.id'],
        name='fk_chapter_document'
    ),
)

meta.create_all(engine)


def insert_project(project_id: int):
    ins = project.insert().values(
        project_id=project_id
    )
    conn = engine.connect()
    return conn.execute(ins)


def insert_document(document_name: str, download_link: str, view_link: str, content_original: bytes or None,
                    project_id: int,
                    extension: str, status=None):
    content_transformed = None

    if status is None:
        if extension == 'docx':
            status = Status.CONVERTED
            content_transformed = content_original
        elif extension == 'pdf':
            status = Status.READY_TO_CONVERT
        else:
            status = Status.INVALID_EXTENSION

    ins = document.insert().values(
        document_name=document_name,
        download_link=download_link,
        view_link=view_link,
        content_original=content_original,
        content_transformed=content_transformed,
        project_id=project_id,
        status=status.value
    )
    conn = engine.connect()
    return conn.execute(ins)


def insert_chapter(text: str, chapter_number: str, chapter_idx: int, header: str, header_preprocessed: str,
                   parent_header: str,
                   parent_preprocessed: str,
                   grandparent_header: str, grandparent_preprocessed: str,
                   document_id: int):
    ins = chapter.insert().values(
        text=text,
        chapter_number=chapter_number,
        chapter_idx=chapter_idx,
        header=header,
        header_preprocessed=header_preprocessed,
        parent_header=parent_header,
        parent_preprocessed=parent_preprocessed,
        grandparent_header=grandparent_header,
        grandparent_preprocessed=grandparent_preprocessed,
        document_id=document_id
    )
    conn = engine.connect()
    return conn.execute(ins)


def insert_word(preprocessed_word, tfidf_score, chapter_ref):
    ins = word.insert().values(
        word=preprocessed_word,
        tfidf=tfidf_score,
        chapter_id=chapter_ref
    )
    conn = engine.connect()
    return conn.execute(ins)


def get_documents_by_status(status: Status):
    query = """
        SELECT id, project_id, content_original 
        FROM document 
        WHERE status = "{0}" 
        """.format(status.value)

    conn = engine.connect()
    return conn.execute(query).fetchall()


def get_transformed_documents_by_project_id(project_id: int):
    query = """
        SELECT id, project_id, content_transformed 
        FROM document 
        WHERE project_id = "{0}"
        AND status = 'converted' 
        """.format(project_id)

    conn = engine.connect()
    return conn.execute(query).fetchall()


def update_status(document_id: int, new_status: Status):
    query = document.update(). \
        values(status=new_status.value). \
        where(document.c.id == document_id)
    conn = engine.connect()
    return conn.execute(query)


def update_content_transformed(document_id: int, transformed: bytes):
    query = document.update(). \
        values(content_transformed=transformed). \
        where(document.c.id == document_id)
    conn = engine.connect()
    return conn.execute(query)


def select_chapter_words_by_score(score: float or None, limit: int or None = None):
    if score is None:
        score = 1
    query = """
        SELECT
  chapter_id,
  text,
  chapter_number,
  header,
  header_preprocessed,
  parent_header,
  parent_preprocessed,
  grandparent_header,
  grandparent_preprocessed,
  document_id,
  group_concat(w.word SEPARATOR ' ') as preprocessed
FROM chapter
  INNER JOIN word w ON chapter.id = w.chapter_id
WHERE score >= {0}
GROUP BY chapter_id
    """.format(score)

    if limit is not None:
        query += ' LIMIT {0}'.format(limit)

    conn = engine.connect()
    return conn.execute(query)


def update_chapter_topic(chapter_id: int, topic_1: dict, topic_2: dict, topic_3: dict, topic_4: dict, topic_5: dict):
    query = chapter.update(). \
        values(
        topic_1_id=topic_1['index'],
        topic_1_value=topic_1['value'],
        topic_2_id=topic_2['index'],
        topic_2_value=topic_2['value'],
        topic_3_id=topic_3['index'],
        topic_3_value=topic_3['value'],
        topic_4_id=topic_4['index'],
        topic_4_value=topic_4['value'],
        topic_5_id=topic_5['index'],
        topic_5_value=topic_5['value'],
    ). \
        where(chapter.c.id == chapter_id)

    conn = engine.connect()
    return conn.execute(query)


def do_query(query: str):
    conn = engine.connect()
    return conn.execute(query)


def insert_trainingdata_from_chapter(chapter, category, round, suggested_label):
    ins = trainingdata.insert().values(
        id=chapter[0],
        text=chapter['text'],
        chapter_idx=chapter['chapter_idx'],
        chapter_number=chapter['chapter_number'],
        header=chapter['header'],
        header_preprocessed=chapter['header_preprocessed'],
        parent_header=chapter['parent_header'],
        parent_preprocessed=chapter['parent_preprocessed'],
        grandparent_header=chapter['grandparent_header'],
        grandparent_preprocessed=chapter['grandparent_preprocessed'],
        topic_1_id=chapter['topic_1_id'],
        topic_1_value=chapter['topic_1_value'],
        topic_2_id=chapter['topic_2_id'],
        topic_2_value=chapter['topic_2_value'],
        topic_3_id=chapter['topic_3_id'],
        topic_3_value=chapter['topic_3_value'],
        topic_4_id=chapter['topic_4_id'],
        topic_4_value=chapter['topic_4_value'],
        topic_5_id=chapter['topic_5_id'],
        topic_5_value=chapter['topic_5_value'],
        document_id=chapter['document_id'],
        category=category,
        round=round,
        suggested_label=suggested_label
    )

    conn = engine.connect()
    return conn.execute(ins)
