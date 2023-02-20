import argparse
import logging
import os
import time

import pandas as pd
import jieba
import streamlit as st
from whoosh import sorting
from whoosh.qparser import QueryParser

from build_index import INDEX_DIR, DummyAnalyzer, build, load, validate

PDF_FILES_DIR = None
OCR_RESULTS_DIR = "ocr_results"
CHROME_EXISTS = False
START_VOL = 38
END_VOL = 55


def get_index():
    if "index" not in st.session_state:
        return None
    return st.session_state.index


def build_index():
    print("building index.")
    st.session_state["index"] = build(quiet=False, show_progress=True)


def load_index():
    print("loading index.")
    st.session_state["index"] = load()


def search(ix, keywords, sorted_by, start_vol, end_vol):
    searcher = ix.searcher()
    content_t_cn_parser = QueryParser("content_t_cn", ix.schema)
    query = content_t_cn_parser.parse(" AND ".join(keywords))

    if sorted_by is None:
        results = searcher.search(query, limit=None, optimize=False)
    else:
        results = searcher.search(
            query, limit=None, optimize=False, sortedby=sorted_by
        )

    hits = []
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
        hits.append(choice)

    return hits


def show_vol_distribution(hits, start_vol, end_vol):
    df = pd.DataFrame(hits, columns=["vol", "page", "side", "content"])
    gb = df.groupby(by="vol", as_index=False).agg(count=("content", 'count'))
    show_plotly(gb, start_vol, end_vol)


def show_plotly(gb, start_vol, end_vol):
    import plotly.graph_objects as go
    colors = ['#FF4B4B'] * len(gb)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=gb['vol'], y=gb['count'], marker_color=colors))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def show_pyplot(gb):
    import matplotlib.pyplot as plt

    vol_min = gb["vol"].min()
    vol_max = gb["vol"].max()
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.bar(gb["vol"], gb["count"], width=0.5, color='#FF4B4B')
    plt.xticks(range(vol_min, vol_max + 1))
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    st.pyplot(fig, clear_figure=True)


def show_results(hits):
    for vol, page, side, content in hits:
        location = f"{vol} 卷 {page - 1} 頁{side}部分"
        if CHROME_EXISTS and PDF_FILES_DIR is not None:
            pdf_file_path = f"file://{PDF_FILES_DIR}/{vol}.pdf#page={page + 1}"
            location = f"[{location}]({pdf_file_path})"
            st.markdown(location)
        else:
            st.write(location)
        st.caption(content)


def highlight(keywords: tuple[str], content: str) -> str:
    for keyword in keywords:
        content = content.replace(keyword, f" **:red[{keyword}]** ")

    return content


def app():
    ix = get_index()
    if ix is None:
        if not os.path.exists(INDEX_DIR):
            st.warning("未發現可用索引，即將開始構建索引，這可能需要 1-2 分鐘")
            build_index()
            st.success("索引構建完成!")
        else:
            st.warning("加載索引中...")
            load_index()
            st.success("加載構建完成!")
            st.info("驗證索引中...")
            passed, expected, actual = validate()
            if passed:
                st.success("驗證功過!")
            else:
                st.error(f"驗證失敗, 預期 {expected} 項, 實際 {actual} 項, 請重建索引")

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

    start_vol, end_vol = st.sidebar.slider(
        "卷號搜索範圍(37 卷之前內容待更新)",
        START_VOL,
        END_VOL,
        (START_VOL, END_VOL)
    )

    if st.sidebar.button("重建索引"):
        st.sidebar.warning("即將開始構建索引，這可能需要 1-2 分鐘")
        build_index()
        st.sidebar.success("索引構建完成!")

    if keywords:
        start = time.time()
        ix = st.session_state.index
        hits = search(ix, keywords, sorted_by, start_vol, end_vol)
        if not hits:
            st.error("未找到匹配結果.")
        else:
            st.success("找到 %d 個匹配結果，用時 %f 秒" % (len(hits), time.time() - start))
            show_vol_distribution(hits, start_vol, end_vol)
            show_results(hits)


if __name__ == "__main__":
    jieba.setLogLevel(logging.ERROR)
    jieba.load_userdict("dict.txt")

    parser = argparse.ArgumentParser(
        description="Qing Manufacturing Office Digital Records Search Engine"
    )
    parser.add_argument("--pdf_files_dir", type=str)
    args = parser.parse_args()

    if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        CHROME_EXISTS = True

    if args.pdf_files_dir is not None:
        PDF_FILES_DIR = os.path.abspath(args.pdf_files_dir)

    app()
