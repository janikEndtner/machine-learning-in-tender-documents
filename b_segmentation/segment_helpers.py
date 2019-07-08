import re
from docx.document import Document as Type_Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Docx_Block:
    def __init__(self, paragraph: Paragraph or None, table: Table or None):
        self.paragraph = paragraph
        self.table = table

    def is_header(self) -> bool:
        return 'Heading' in self.get_element_style_name()

    def get_element_style_name(self) -> str:

        if self.paragraph is not None:
            return self.paragraph.style.name
        else:
            return self.table.style.name

    def to_string(self) -> str:
        # if it's a table
        if self.table is not None:
            return self.table_to_string()
        else:
            return self.paragraph_to_string()

    def table_to_string(self) -> str:
        _text = 'table: \n'
        for row in self.table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _text += paragraph.text
                _text += " | "
            _text += "\n"
        return _text + '\n'

    def paragraph_to_string(self) -> str:
        return replace_line_delimiter(self.paragraph.text).replace("\n", "") + '\n'


# remove line delimiter and following white char
def replace_line_delimiter(text):
    match = re.search(r'-\s[a-z]', text)
    if match:
        text = re.sub(r'-\s[a-z]', match.group()[-1], text)
    return text


# remove line break without text if more than one in a row
def remove_unnecessary_line_breaks(parts):
    processed = []
    for p in parts:
        if p.is_empty() and len(processed) > 0:
            processed[-1].set_ends_with_big_break(True)
        elif not p.is_empty():
            processed.append(p)
    return processed


def iter_block_items(parent):
    """
    Yield each paragraph and table child within *parent*, in document
    order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, Type_Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Docx_Block(Paragraph(child, parent), None)
        elif isinstance(child, CT_Tbl):
            yield Docx_Block(None, Table(child, parent))


def get_cosine_sim(list_a, list_b):
    list_a = '<space>'.join(list(map(lambda x: '<space>'.join(x), list_a)))
    list_b = '<space>'.join(list(map(lambda x: '<space>'.join(x), list_b)))
    corpus = [list_a, list_b]
    vectorizer = CountVectorizer(tokenizer=lambda x: x.split("<space>"))
    X = vectorizer.fit_transform(corpus)

    return cosine_similarity(X)[0, 1]


def find_project_id_in_path(path, prefix):
    # replace for windows paths
    path = path.replace('\\', '/')
    start = path.index(prefix) + len(prefix)
    end = path.index('__')
    return path[start: end]