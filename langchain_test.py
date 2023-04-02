import os
import json

from langchain import VectorDBQA
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAIChat
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


PERSIST_DIR= "chroma.db"
OPENAPI_API_KEY = ""
os.environ['OPENAI_API_KEY'] = OPENAPI_API_KEY


def build_doc():
    ocr_results_path = "./ocr_results"
    chars = []
    for f in os.listdir(ocr_results_path):
        if f.startswith("50_"):
            with open(os.path.join(ocr_results_path, f)) as fd:
                j = json.load(fd)
                chars.append("".join(j["chars"]))
    with open("50.txt", "w") as fd:
        fd.write("\n\n".join(chars))


def build_index():
    loader = TextLoader("50.txt")
    doc = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    texts = text_splitter.split_documents(doc)

    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAPI_API_KEY)

    vectordb = Chroma.from_documents(texts, embeddings, persist_directory=PERSIST_DIR)
    vectordb.persist()


def load_index():
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAPI_API_KEY)
    vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    qa = VectorDBQA.from_chain_type(llm=OpenAIChat(), chain_type="stuff", vectorstore=vectordb)
    return qa


def query(q: str, qa: "BaseRetrievalQA"):
    print(qa({"query": q})["result"])


if __name__ == '__main__':
    qa = load_index()
    while True:
        inp = input("query: ")
        query(inp, qa)
