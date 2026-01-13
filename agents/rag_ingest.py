from pathlib import Path
from tempfile import mkdtemp

import tiktoken
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from docling.chunking import HybridChunker
from langchain_docling import DoclingLoader

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from urllib.parse import urlparse

from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from utils.file_io import read_markdown_file


def create_vectorstore(
    FILE_PATH: str,
    TOP_K: int = 3,
    chroma_server_url: str | None = None,
    collection_name: str = "vectordb",
    drop_old: bool = False,
):
    """
    Ingest a single file into a Chroma vector store and return a retriever.

    Notes:
    - By default this uses a temporary local path which will not preserve data.
      Pass a persistent `chroma_server_url` (e.g., http://chroma:8000) if you want
      embeddings to be preserved across runs.
    - Set `drop_old=True` only when you intend to recreate the collection.
    """

    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    enc = tiktoken.get_encoding("cl100k_base")
    tokenizer = OpenAITokenizer(tokenizer=enc, max_tokens=128 * 1024)

    loader = DoclingLoader(
        file_path=FILE_PATH, chunker=HybridChunker(tokenizer=tokenizer)
    )
    docs = loader.load()

    # Use Chroma server if URL provided, otherwise use local persistent directory
    if chroma_server_url:
        # Parse the URL to extract host and port
        parsed = urlparse(chroma_server_url)
        host = parsed.hostname or "chroma"
        port = parsed.port or 8000
        
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            collection_name=collection_name,
            client_settings={
                "chroma_server_host": host,
                "chroma_server_http_port": port,
            },
        )
    else:
        # Local persistent storage
        persist_directory = str(Path(mkdtemp()) / "chroma_db")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            collection_name=collection_name,
            persist_directory=persist_directory,
        )

    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    return retriever


def create_rag_chain(retriever: VectorStoreRetriever):
    """Create a Retrieval-Augmented Generation (RAG) chain using the provided retriever."""

    prompts_dir = Path(__file__).resolve().parent / "prompts"
    PROMPT = PromptTemplate.from_template(
        read_markdown_file(str(prompts_dir / "retriever_prompt.md"))
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain


def add_file_to_existing_vectorstore(
    FILE_PATH: str, vectorstore: Chroma, TOP_K: int = 3
):
    """
    Add a file's chunks into an existing Chroma vector store.

    This preserves previously ingested embeddings by appending new documents.
    Returns a retriever for convenience.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokenizer = OpenAITokenizer(tokenizer=enc, max_tokens=128 * 1024)
    loader = DoclingLoader(
        file_path=FILE_PATH, chunker=HybridChunker(tokenizer=tokenizer)
    )
    docs = loader.load()

    # Append new documents to the existing store
    vectorstore.add_documents(docs)
    return vectorstore.as_retriever(search_kwargs={"k": TOP_K})


def initialize_vectorstore_with_rag_chain(
    FILE_PATH: str,
    TOP_K: int = 3,
    *,
    chroma_server_url: str | None = None,
    collection_name: str = "vectordb",
    drop_old: bool = False,
):
    """
    Convenience: ingest a file into the vector store and return a RAG chain.
    Control persistence via `chroma_server_url` and collection behavior via `drop_old`.
    """
    retriever = create_vectorstore(
        FILE_PATH,
        TOP_K,
        chroma_server_url=chroma_server_url,
        collection_name=collection_name,
        drop_old=drop_old,
    )
    return create_rag_chain(retriever)


def upload_file_with_rag_chain(FILE_PATH: str, vectorstore: Chroma, TOP_K: int = 3):
    retriever = add_file_to_existing_vectorstore(FILE_PATH, vectorstore, TOP_K)
    return create_rag_chain(retriever)
