import json
import mimetypes
import os
import shutil
import time
from pathlib import Path
from typing import Dict

import fitz
import requests
from split_image import split_image

# TODO: other volumes
VOL_TO_START_PAGE_NUM: Dict[int, int] = {
    39: 30,
    40: 26,
    41: 24,
    42: 22,
    43: 20,
    44: 36,
    45: 30,
    46: 24,
    47: 18,
    48: 16,
    49: 18,
    50: 20,
    51: 26,
    52: 28,
    53: 35,
    54: 62,
    55: 52,
}
PDF_FILES_DIR = "pdf_files"
TEMP_DIR = "temp"
OCR_RESULTS_DIR = "ocr_results"
OCR_ENDPOINT = "https://api.jzd.cool:9013/ocr_pro"
OCR_ENDPOINT_2 = "https://ocr.gj.cool/ocr_pro"
APIID = ""
PASSWORD = ""
TOKEN = None
LAST_AUTH_DATETIME = None
IGNORE_FAILURE = True


def process_vol(file_name: str):
    vol = int(file_name[:-4])
    pdf_document = fitz.Document(f"{PDF_FILES_DIR}/{file_name}")
    for page_num in range(VOL_TO_START_PAGE_NUM[vol], pdf_document.page_count):
        page = pdf_document[page_num]
        print(
            "processing vol %d, page %d, progress %.2f %%"
            % (vol, page_num, 100 * page_num / pdf_document.page_count)
        )
        if not process_page(page, vol):
            break


def process_page(pg: fitz.Page, vol: int) -> bool:
    page_path = f"{TEMP_DIR}/{vol}_{pg.number}.jpg"

    ocr_result_0_path = f"{OCR_RESULTS_DIR}/{vol}_{pg.number}_0.json"
    ocr_result_1_path = f"{OCR_RESULTS_DIR}/{vol}_{pg.number}_1.json"
    if os.path.exists(ocr_result_0_path) and os.path.exists(ocr_result_1_path):
        print(f"\t{ocr_result_0_path} exists")
        print(f"\t{ocr_result_1_path} exists")
        return True

    start_time = time.time()
    pg.get_pixmap(dpi=500).save(page_path)
    split_image(page_path, 2, 1, True, False, should_quiet=True, output_dir=TEMP_DIR)
    print(f"\timages generated, elapsed time {round(time.time() - start_time)} s")

    start_time = time.time()
    split_0_path = f"{TEMP_DIR}/{vol}_{pg.number}_0.jpg"
    if not ocr(split_0_path, ocr_result_0_path):
        return False

    time.sleep(5)

    split_1_path = f"{TEMP_DIR}/{vol}_{pg.number}_1.jpg"
    if not ocr(split_1_path, ocr_result_1_path):
        return False
    print(f"\tocr done, elapsed time {round(time.time() - start_time)} s")

    os.remove(page_path)
    os.remove(split_0_path)
    os.remove(split_1_path)
    return True


def ocr(page_path: str, ocr_result_path: str) -> bool:
    if not authorize():
        return False

    if os.path.exists(ocr_result_path):
        print(f"\t{ocr_result_path} exists")
        return True

    start_time = time.time()
    continue_ = True
    while continue_:
        try:
            resp = request(page_path, OCR_ENDPOINT)
            resp_json = json.loads(resp.text)

            if "msg" in resp_json:
                msg = resp_json["msg"]
                print(f"\trequest failed with msg {msg}")
                continue_ = IGNORE_FAILURE
                time.sleep(15)
            else:
                continue_ = False
        except Exception as e:
            print(f"\trequest failed due to {e}")
            continue_ = IGNORE_FAILURE
            time.sleep(15)
            continue

    with open(ocr_result_path, "w") as fd:
        fd.write(resp.text)

    print(
        f"\tocr on {page_path} done, elapsed time {round(time.time() - start_time)} s"
    )
    return True


def authorize() -> bool:
    global LAST_AUTH_DATETIME
    global TOKEN

    if LAST_AUTH_DATETIME is not None and time.time() - LAST_AUTH_DATETIME < 3000:
        return True

    payload = {"apiid": APIID, "password": PASSWORD}
    resp = requests.request(
        "POST", "https://ocr.gj.cool/ocr_login", headers={}, data=payload
    )
    j = json.loads(resp.text)
    if "msg" in j:
        msg = j["msg"]
        print(f"\tauth failed with msg {msg}")
        return False
    else:
        token = j["access_token"]
        TOKEN = f"gjcool {token}"
        LAST_AUTH_DATETIME = time.time()
        return True


def request(page_path: str, endpoint: str) -> requests.Response:
    headers = {"Authorization": TOKEN}
    mime, _ = mimetypes.guess_type(page_path)
    filename = Path(page_path).stem
    files = [("img", (filename, open(page_path, "rb"), mime))]
    payload = {"layout": 0, "area": "[]"}
    return requests.request(
        "POST", endpoint, headers=headers, data=payload, files=files
    )


if __name__ == "__main__":
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.mkdir(TEMP_DIR)

    if not os.path.exists(OCR_RESULTS_DIR):
        os.mkdir(OCR_RESULTS_DIR)

    for f in os.listdir(PDF_FILES_DIR):
        process_vol(f)

    shutil.rmtree(TEMP_DIR)
