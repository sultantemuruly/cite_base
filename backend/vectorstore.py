import os
from uuid import uuid4
from urllib.parse import urlparse
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Get ChromaDB connection details from environment
chroma_url = os.getenv("CHROMA_SERVER_URL", "http://localhost:1234")
parsed_url = urlparse(chroma_url)
chroma_host = parsed_url.hostname or "localhost"
chroma_port = parsed_url.port or 1234

client = chromadb.HttpClient(host=chroma_host, port=chroma_port, ssl=False)
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
