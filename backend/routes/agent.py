from fastapi import APIRouter, HTTPException, Depends
from agents.orchestration import graph, MainState

from models import Docs
from dependencies import SessionDep
from vectorstore import create_rag_chain_for_documents

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/status")
def get_agent_status():
    return {"status": "Agent route is working"}


@router.post("/execute")
def execute_agent_task(user_question: str, doc_id: int, db_session: SessionDep):
    """Execute the agent task based on user question and document ID."""
    doc = db_session.query(Docs).filter(Docs.id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=404, detail=f"Document with id {doc_id} not found"
        )

    doc_uuids = doc.document_uuids

    # Create RAG chain for the specific documents
    rag_chain = create_rag_chain_for_documents(doc_uuids, top_k=3)
    state = MainState(question=user_question, rag_chain=rag_chain)
    result = graph.invoke(state)

    final_answer = result.get("final_answer", "No answer generated.")
    return {"final_answer": final_answer}
