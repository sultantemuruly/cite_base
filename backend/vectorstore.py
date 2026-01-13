from uuid import uuid4
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
client = chromadb.HttpClient(host="localhost", port=1234, ssl=False)
collection = client.get_or_create_collection("citebase_collection")

vector_store = Chroma(
    client=client,
    collection_name="citebase_collection",
    embedding_function=embeddings,
)


def get_documents(ids: list[str]) -> list[Document]:
    return vector_store.get(ids=ids)


def upload_documents(documents: list[Document]):
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    return uuids


def delete_documents(ids: list[str]):
    vector_store.delete_documents(ids=ids)


def update_documents(documents: list[Document], ids: list[str]):
    vector_store.update_documents(ids=ids, documents=documents)
