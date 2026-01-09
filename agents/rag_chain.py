from pathlib import Path
from tempfile import mkdtemp

from agents.rag_ingest import initialize_vectorstore_with_rag_chain

FILE_PATH = "https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
TOP_K = 3
milvus_uri = str(Path(mkdtemp()) / "vector.db")
collection_name = "vectordb"

rag_chain = initialize_vectorstore_with_rag_chain(
    FILE_PATH=FILE_PATH,
    TOP_K=TOP_K,
    milvus_uri=milvus_uri,
    collection_name=collection_name,
)
