import argparse
import logging
import os
import time

import jieba
import streamlit as st
from whoosh import sorting
from whoosh.qparser import QueryParser

from build_index import INDEX_DIR, DummyAnalyzer, build

PDF_FILES_DIR = None
OCR_RESULTS_DIR = "ocr_results"
CHROME_EXISTS = False


def build_index(force: bool):
    if "index" not in st.session_state:
        if force:
            print("rebuilding index.")
        else:
            print("loading existing index.")
        ix = build(force, quiet=False, show_progress=True)
        st.session_state["index"] = ix
        return ix
    else:
        print("using cached index.")
        return st.session_state.index


def highlight(keywords: tuple[str], content: str) -> str:
    for keyword in keywords:
        content = content.replace(keyword, f" **:red[{keyword}]** ")

    return content


def app():
    if not os.path.exists(INDEX_DIR):
        st.warning("未發現可用索引，即將開始構建索引，這可能需要 1-2 分鐘")
        build_index(force=True)
        st.success("索引構建完成!")
    else:
        build_index(force=False)

    st.subheader("清宮造辦處電子檔案搜索系統")
    keywords = st.sidebar.text_input("請以 **繁體中文** 輸入待查詢內容:")
    keywords = keywords.split()

    order = st.sidebar.selectbox("匹配結果排序方式:", ("相關性", "時間"))
    sorted_by = None
    if order == "時間":
        reverse = st.sidebar.checkbox("匹配結果反向排序")
        vol_facet = sorting.FieldFacet("vol", reverse=reverse)
        page_facet = sorting.FieldFacet("page", reverse=reverse)
        side_facet = sorting.FieldFacet("side", reverse=reverse)
        sorted_by = [vol_facet, page_facet, side_facet]

    start_vol, end_vol = st.sidebar.slider("卷號搜索範圍(37 卷之前內容待更新)", 38, 55, (38, 55))

    if keywords:
        ix = st.session_state.index
        searcher = ix.searcher()
        content_t_cn_parser = QueryParser("content_t_cn", ix.schema)
        query = content_t_cn_parser.parse(" AND ".join(keywords))

        start = time.time()
        if sorted_by is None:
            results = searcher.search(query, limit=None, optimize=False)
        else:
            results = searcher.search(
                query, limit=None, optimize=False, sortedby=sorted_by
            )

        choices = []
        for hit in results:
            vol = hit["vol"]
            vol = int(vol)
            if vol < start_vol or vol > end_vol:
                continue
            page = int(hit["page"])
            side = "上半" if hit["side"] == "0" else "下半"
            content: str = hit["content_raw"]
            content = " ".join(list(jieba.cut(content, cut_all=False)))
            content = highlight(keywords, content)

            choice = (vol, page, side, content)
            choices.append(choice)

        if not choices:
            st.error("未找到匹配結果.")
        else:
            st.success("找到 %d 個匹配結果，用時 %f 秒" % (len(choices), time.time() - start))

        for vol, page, side, content in choices:
            location = f"{vol} 卷 {page - 1} 頁{side}部分"
            if CHROME_EXISTS and PDF_FILES_DIR:
                pdf_file_path = f"file://{PDF_FILES_DIR}/{vol}.pdf#page={page + 1}"
                location = f"[{location}]({pdf_file_path})"
                st.markdown(location)
            else:
                st.write(location)
            st.caption(content)


if __name__ == "__main__":
    jieba.setLogLevel(logging.ERROR)
    jieba.load_userdict("dict.txt")

    parser = argparse.ArgumentParser(
        description="Qing Manufacturing Office Digital Records Search Engine"
    )
    parser.add_argument('--pdf_files_dir', type=str)
    args = parser.parse_args()

    if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        CHROME_EXISTS = True

    PDF_FILES_DIR = os.path.abspath(args.pdf_files_dir)

    app()
