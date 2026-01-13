from fastapi import APIRouter

from langchain_core.documents import Document

from vectorstore import (
    upload_documents as upload_to_vectorstore,
    get_documents as get_from_vectorstore,
    delete_documents as delete_from_vectorstore,
    update_documents as update_in_vectorstore,
)
from dependencies import SessionDep, CurrentUser
from models import Docs

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/status")
def get_documents_status():
    return {"status": "Documents route is working"}


@router.get("/get")
def get_documents(ids: list[str]):
    try:
        documents = get_from_vectorstore(ids)
        docs = [doc.dict() for doc in documents]
        return {"status": "success", "documents": docs}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/upload")
def upload_documents(
    documents: list[Document],
    db_session: SessionDep,
    current_user: CurrentUser,
):
    try:
        # Upload documents to vector store
        uuids = upload_to_vectorstore(documents)
        
        # Save document UUIDs to database with user_id
        db_docs = [
            Docs(user_id=current_user.id, document_uuid=doc_uuid)
            for doc_uuid in uuids
        ]
        db_session.add_all(db_docs)
        db_session.commit()
        
        return {"status": "success", "ids": uuids}
    except Exception as e:
        db_session.rollback()
        return {"status": "error", "message": str(e)}


@router.delete("/delete")
def delete_documents(ids: list[str]):
    try:
        delete_from_vectorstore(ids)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/update")
def update_documents(documents: list[Document], ids: list[str]):
    try:
        update_in_vectorstore(documents, ids)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
