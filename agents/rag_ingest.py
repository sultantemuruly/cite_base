from pathlib import Path
from tempfile import mkdtemp

import tiktoken
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from docling.chunking import HybridChunker
from langchain_docling import DoclingLoader

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from langchain_core.vectorstores import VectorStoreRetriever

from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


def read_markdown_file(filepath):
    """Reads the content of a Markdown file as a string."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    except FileNotFoundError:
        return f"Error: The file at {filepath} was not found."
    except Exception as e:
        return f"An error occurred: {e}"


def create_vectorstore(
    FILE_PATH: str,
    TOP_K: int = 3,
    milvus_uri: str | None = None,
    collection_name: str = "vectordb",
    drop_old: bool = False,
):
    """
    Ingest a single file into a Milvus vector store and return a retriever.

    Notes:
    - By default this uses a temporary local URI which will not preserve data.
      Pass a persistent `milvus_uri` (e.g., a Milvus server URI) if you want
      embeddings to be preserved across runs.
    - Set `drop_old=True` only when you intend to recreate the collection.
    """

    embedding = OpenAIEmbeddings(model="text-embedding-3-large")

    enc = tiktoken.get_encoding("cl100k_base")
    tokenizer = OpenAITokenizer(tokenizer=enc, max_tokens=128 * 1024)

    loader = DoclingLoader(
        file_path=FILE_PATH, chunker=HybridChunker(tokenizer=tokenizer)
    )
    docs = loader.load()

    # Default to a temp path if no URI is provided (ephemeral storage)
    effective_uri = milvus_uri or str(Path(mkdtemp()) / "vector.db")

    vectorstore = Milvus.from_documents(
        documents=docs,
        embedding=embedding,
        collection_name=collection_name,
        connection_args={"uri": effective_uri},
        index_params={"index_type": "FLAT"},
        drop_old=drop_old,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    return retriever


def create_rag_chain(retriever: VectorStoreRetriever):
    """Create a Retrieval-Augmented Generation (RAG) chain using the provided retriever."""

    prompts_dir = Path(__file__).resolve().parent / "prompts"
    PROMPT = PromptTemplate.from_template(
        read_markdown_file(str(prompts_dir / "retriever_prompt.md"))
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain


def add_file_to_existing_vectorstore(
    FILE_PATH: str, vectorstore: Milvus, TOP_K: int = 3
):
    """
    Add a file's chunks into an existing Milvus vector store.

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
    milvus_uri: str | None = None,
    collection_name: str = "vectordb",
    drop_old: bool = False,
):
    """
    Convenience: ingest a file into the vector store and return a RAG chain.
    Control persistence via `milvus_uri` and collection behavior via `drop_old`.
    """
    retriever = create_vectorstore(
        FILE_PATH,
        TOP_K,
        milvus_uri=milvus_uri,
        collection_name=collection_name,
        drop_old=drop_old,
    )
    return create_rag_chain(retriever)


def upload_file_with_rag_chain(FILE_PATH: str, vectorstore: Milvus, TOP_K: int = 3):
    retriever = add_file_to_existing_vectorstore(FILE_PATH, vectorstore, TOP_K)
    return create_rag_chain(retriever)
