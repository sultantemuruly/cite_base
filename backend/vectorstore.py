import os
from uuid import uuid4
from urllib.parse import urlparse
from pathlib import Path
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from utils.file_io import read_markdown_file

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


def create_rag_chain_for_documents(document_uuids: list[str], top_k: int = 3):
    """Create a RAG chain that only retrieves from specific document UUIDs."""

    # Create a custom retriever that works with specific document IDs
    def custom_retriever(query: str) -> list[Document]:
        query_embedding = embeddings.embed_query(query)

        # Use ChromaDB client directly to query only specific documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, len(document_uuids)),
            where_document=None,  # No text filter
            include=["documents", "metadatas", "distances"],
        )

        if not results or "documents" not in results or not results["documents"]:
            all_docs_result = collection.get(
                ids=document_uuids, include=["documents", "metadatas"]
            )
            if all_docs_result and "documents" in all_docs_result:
                docs = []
                for i, doc_text in enumerate(all_docs_result["documents"][:top_k]):
                    metadata = (
                        all_docs_result["metadatas"][i]
                        if "metadatas" in all_docs_result
                        and i < len(all_docs_result["metadatas"])
                        else {}
                    )
                    docs.append(Document(page_content=doc_text, metadata=metadata))
                return docs
            return []

        docs = []
        for i, doc_text in enumerate(results["documents"][0]):
            metadata = (
                results["metadatas"][0][i]
                if "metadatas" in results
                and results["metadatas"]
                and i < len(results["metadatas"][0])
                else {}
            )
            # Filter to only include our target document UUIDs
            doc_id = (
                results["ids"][0][i]
                if "ids" in results and results["ids"] and i < len(results["ids"][0])
                else None
            )
            if doc_id in document_uuids:
                docs.append(Document(page_content=doc_text, metadata=metadata))

        return docs[:top_k]

    # Load the prompt template
    try:

        prompts_dir = Path(__file__).resolve().parent / "agents" / "prompts"
        prompt_text = read_markdown_file(str(prompts_dir / "retriever_prompt.md"))
    except:
        # Fallback prompt if file not found
        prompt_text = """Answer the question based only on the following context:

{context}

Question: {question}

Answer:"""

    prompt = PromptTemplate.from_template(prompt_text)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create RAG chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": lambda x: format_docs(custom_retriever(x["question"])),
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
