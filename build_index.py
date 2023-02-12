import json
import os
import shutil
from typing import TYPE_CHECKING

import jieba
from jieba.analyse import ChineseAnalyzer
from whoosh.analysis import Token, Tokenizer
from whoosh.fields import NUMERIC, TEXT, Schema
from whoosh.index import create_in, open_dir
from zhconv import convert

from ocr import OCR_RESULTS_DIR

if TYPE_CHECKING:
    from whoosh.index import Index


INDEX_DIR = "index"
PROB_THRESHOLD = 0.2


class DummyAnalyzer(Tokenizer):
    def __call__(self, text, **kargs):
        words = list(text)
        cur_pos = 0
        for word in words:
            token = Token()
            token.original = token.text = word
            token.pos = cur_pos
            token.startchar = cur_pos
            token.endchar = cur_pos
            cur_pos += 1
            yield token


def validate():
    ix = open_dir(INDEX_DIR)
    expected = len(os.listdir(OCR_RESULTS_DIR))
    actual = ix.searcher().doc_count()
    return actual == expected, expected, actual


def load():
    return open_dir(INDEX_DIR)


def build(quiet: bool = False, show_progress: bool = False) -> "Index":
    shutil.rmtree(INDEX_DIR, ignore_errors=True)
    jieba.load_userdict("dict.txt")
    analyzer = ChineseAnalyzer()
    schema = Schema(
        vol=NUMERIC(stored=True, sortable=True),
        page=NUMERIC(stored=True, sortable=True),
        side=NUMERIC(stored=True, sortable=True),
        content_t_cn=TEXT(stored=True, analyzer=analyzer),
        content_s_cn=TEXT(stored=True, analyzer=analyzer),
        content_raw=TEXT(stored=True, analyzer=DummyAnalyzer()),
    )
    os.mkdir(INDEX_DIR)
    ix = create_in(INDEX_DIR, schema)
    _build(ix, quiet, show_progress)
    return ix


def _build(idx: "Index", quiet: bool, show_progress: bool):
    writer = idx.writer()
    files = os.listdir(OCR_RESULTS_DIR)

    progress_bar = None
    if show_progress:
        import streamlit as st

        st.info("構建索引中...")
        progress_bar = st.progress(0)

    for i in range(len(files)):
        f = files[i]
        if not f.endswith(".json"):
            continue

        if not quiet:
            progress = float(i) / len(files)
            print(f"{f}, progress: {i} / {len(files)}")
            if progress_bar is not None:
                progress_bar.progress(progress, text=f"({i} / {len(files)})")

        with open(f"{OCR_RESULTS_DIR}/{f}") as fd:
            j = json.load(fd)

        chars = []
        for char_id in j["char_ids"]:
            if j["char_probs"][char_id] > PROB_THRESHOLD:
                chars.append(j["chars"][char_id])

        content_t_cn = "".join(chars)
        content_s_cn = convert(content_t_cn, "zh-cn")
        vol, page, side = f[:-5].split("_")
        writer.add_document(
            vol=vol,
            page=page,
            side=side,
            content_t_cn=content_t_cn,
            content_s_cn=content_s_cn,
            content_raw=content_t_cn,
        )
    writer.commit()


if __name__ == "__main__":
    build(quiet=False)
