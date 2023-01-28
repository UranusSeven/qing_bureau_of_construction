import os.path
from textwrap import wrap

import fitz
import jieba
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PyInquirer import prompt
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import logging

from build_index import INDEX_DIR, DummyAnalyzer

PDF_FILES_DIR = "pdf_files"
OCR_RESULTS_DIR = "ocr_results"
TEMP_DIR = "temp"

INPUT = [
    {
        "type": "input",
        "name": "inp",
        "message": "請以 *繁體中文* 輸入待查詢內容, 或輸入 q 退出:",
    },
]


if __name__ == "__main__":
    jieba.setLogLevel(logging.ERROR)
    jieba.load_userdict("dict.txt")

    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    ix = open_dir(INDEX_DIR)
    searcher = ix.searcher()
    content_t_cn_parser = QueryParser("content_t_cn", ix.schema)
    # content_s_cn_parser = QueryParser("content_s_cn", ix.schema)
    content_raw_parser = QueryParser("content_raw", ix.schema)

    while True:
        for f in os.listdir(TEMP_DIR):
            os.remove(f"{TEMP_DIR}/{f}")

        try:
            inp_answer = prompt(INPUT)
        except EOFError:
            break
        else:
            inp = inp_answer.get("inp")
            if inp in ("q", "exit", "quit", None):
                break

        if len(inp) == 1:
            query = content_raw_parser.parse(inp)
        else:
            query = content_t_cn_parser.parse(inp)

        cont = True
        start_page = 1
        while cont:
            cont = False
            results = searcher.search_page(query, pagenum=start_page, pagelen=10)
            choices = []
            choice_to_hit = {}
            for hit in results:
                vol = hit["vol"]
                page = hit["page"]
                content: str = hit["content_raw"]
                content = " ".join(list(jieba.cut(content, cut_all=False)))
                side = "上半" if hit["side"] == "0" else "下半"
                content = "\n".join(list(wrap(content)))
                choice = f"[{hit.rank}] {vol} 卷 {int(page) - 1} 頁 {side} 部分\n{content}"
                choice_to_hit[choice] = hit
                choices.append(choice)
            if results.pagenum < results.pagecount:
                choices.append("下一頁")
            choices.append("退出")
            options = [
                {
                    "type": "list",
                    "name": "choice",
                    "message": f"第 {results.pagenum} 页, 共 {results.pagecount} 頁, 選中按 *enter* 打開對應頁",
                    "choices": choices,
                },
            ]
            choice_answer = prompt(options)
            choice = choice_answer.get("choice")
            if choice == "退出":
                break
            elif choice == "下一頁":
                start_page += 1
                cont = True
            elif choice is None:
                cont = True
            else:
                hit = choice_to_hit[choice]
                vol = hit["vol"]
                page = hit["page"]
                side = hit["side"]

                pdf_file_path = f"{PDF_FILES_DIR}/{vol}.pdf"
                temp_img_path = f"{TEMP_DIR}/{vol}_{page}.jpg"
                pdf_document = fitz.Document(pdf_file_path)
                pdf_page = pdf_document[int(page)]
                pdf_page.get_pixmap(dpi=500).save(temp_img_path)

                img = mpimg.imread(temp_img_path)
                plt.figure(figsize=(8, 11))
                plt.imshow(img)
                plt.show()
                cont = True
