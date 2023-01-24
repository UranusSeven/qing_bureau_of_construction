import os
from whoosh.index import create_in, open_dir
from whoosh.fields import NUMERIC, TEXT, Schema
from jieba.analyse import ChineseAnalyzer


INDEX_DIR = "index"


def initialize():
    if os.path.exists(INDEX_DIR):
        return open_dir(INDEX_DIR)

    analyzer = ChineseAnalyzer()
    schema = Schema(
        vol=NUMERIC(stored=False),
        page=NUMERIC(stored=False),
        content=TEXT(stored=True, analyzer=analyzer),
    )
    os.mkdir(INDEX_DIR)
    return create_in(INDEX_DIR, schema)


if __name__ == "__main__":
    pass
