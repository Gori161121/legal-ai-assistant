from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Legal AI Assistant API",
    description="Prototype API for legal document intelligence, knowledge retrieval and workflow support.",
    version="0.1.0"
)

class LegalDocument(BaseModel):
    id: int
    title: str
    document_type: str
    status: str

class CaseRecord(BaseModel):
    id: int
    client_name: str
    case_type: str
    status: str

documents = [
    LegalDocument(id=1, title="Service Agreement", document_type="contract", status="reviewed"),
    LegalDocument(id=2, title="Privacy Policy", document_type="policy", status="pending")
]

cases = [
    CaseRecord(id=1, client_name="ABC Company", case_type="commercial", status="active"),
    CaseRecord(id=2, client_name="XYZ Ltd", case_type="compliance", status="open")
]

@app.get("/")
def root():
    return {
        "project": "Legal AI Assistant",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents", response_model=List[LegalDocument])
def get_documents():
    return documents

@app.get("/cases", response_model=List[CaseRecord])
def get_cases():
    return cases

@app.get("/legal/summary")
def legal_summary():
    return {
        "total_documents": len(documents),
        "total_cases": len(cases),
        "pending_documents": len([d for d in documents if d.status == "pending"]),
        "recommendation": "Prioritize pending document review and monitor active cases."
    }

@app.get("/knowledge/search")
def knowledge_search(query: str = "contract"):
    return {
        "query": query,
        "results": [
            "Service Agreement",
            "Privacy Policy"
        ],
        "summary": "Relevant legal knowledge retrieved successfully."
    }
