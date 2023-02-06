import logging
import os

import jieba
import streamlit as st
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from build_index import INDEX_DIR, DummyAnalyzer


PDF_FILES_DIR = "pdf_files"
OCR_RESULTS_DIR = "ocr_results"
CHROME_EXISTS = False


def highlight(keywords: tuple[str], content: str) -> str:
    for keyword in keywords:
        content = content.replace(keyword, f" **:red[{keyword}]** ")

    return content


def open_pdf(vol: int, page: int):
    pass


def app():
    st.title("清宮造辦處電子檔案搜索系統")
    keywords = st.text_input('請以 **繁體中文** 輸入待查詢內容:')
    keywords = keywords.split()

    if keywords:
        query = content_t_cn_parser.parse(" AND ".join(keywords))
        results = searcher.search(query, limit=None, optimize=False)

        if not results:
            st.write("未找到匹配結果.")

        choices = []
        for hit in results:
            vol = hit["vol"]
            page = hit["page"]
            side = "上半" if hit["side"] == "0" else "下半"
            content: str = hit["content_raw"]
            content = " ".join(list(jieba.cut(content, cut_all=False)))
            content = highlight(keywords, content)

            choice = (vol, page, side, content)
            choices.append(choice)

        for vol, page, side, content in choices:
            location = f"{vol} 卷 {int(page) - 1} 頁{side}部分"
            if CHROME_EXISTS:
                pdf_file_path = f"file://{PDF_FILES_DIR}/{vol}.pdf#page={int(page) + 1}"
                location = f"[{location}]({pdf_file_path})"
                st.markdown(location)
            else:
                st.write(location)
            st.caption(content)


if __name__ == '__main__':
    jieba.setLogLevel(logging.ERROR)
    jieba.load_userdict("dict.txt")

    ix = open_dir(INDEX_DIR)
    searcher = ix.searcher()
    content_t_cn_parser = QueryParser("content_t_cn", ix.schema)

    if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        CHROME_EXISTS = True

    PDF_FILES_DIR = os.path.join(os.path.dirname(__file__), PDF_FILES_DIR)

    app()