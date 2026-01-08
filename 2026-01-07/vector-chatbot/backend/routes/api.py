from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from database.models import DocumentCreate, QueryRequest
from services.embedding_service import EmbeddingService
from database.chroma_client import ChromaClient
from services.rag_service import RAGService

router = APIRouter()
db_client = ChromaClient()
embedding_service = EmbeddingService()
rag_service = RAGService()

# Sample document content about Renewable Energy
SAMPLE_DOCUMENTS = [
    {
        "content": """Solar energy is harnessed from the sun's radiation using photovoltaic cells. 
        These cells convert sunlight directly into electricity through the photovoltaic effect. 
        Modern solar panels have efficiency rates between 15-22%, with newer technologies promising up to 30% efficiency.
        The cost of solar energy has dropped by 90% in the last decade, making it one of the cheapest energy sources.""",
        "metadata": {"source": "energy_guide", "topic": "solar", "pages": 1}
    },
    {
        "content": """Wind energy utilizes wind turbines to convert kinetic energy from wind into electrical power. 
        Onshore wind farms are typically cheaper to build, while offshore wind farms provide more consistent wind speeds. 
        A single large wind turbine can power up to 600 homes. Wind energy accounts for approximately 7% of global electricity generation.""",
        "metadata": {"source": "energy_guide", "topic": "wind", "pages": 2}
    },
    {
        "content": """Hydropower is the largest source of renewable electricity globally, providing about 16% of world electricity. 
        It works by capturing the energy of flowing water using dams or run-of-river systems. 
        Pumped-storage hydropower acts as a battery, storing energy by pumping water uphill during low demand and releasing it during peak demand.""",
        "metadata": {"source": "energy_guide", "topic": "hydropower", "pages": 3}
    },
    {
        "content": """Cascade Policies in resource management refer to hierarchical decision-making structures where policies at higher levels influence or determine policies at lower levels. 
        For example, national energy policies cascade down to state regulations, which then inform local implementation rules. 
        This ensures alignment across different governance levels but can sometimes create implementation gaps or conflicts between different policy layers.""",
        "metadata": {"source": "policy_guide", "topic": "governance", "pages": 4}
    }
]

@router.post("/documents/")
async def create_document(doc: DocumentCreate):
    """Create a new document with vector embedding"""
    doc_id = str(uuid.uuid4())
    
    # Generate embedding
    embedding = embedding_service.generate_embedding(doc.content)
    
    # Store in ChromaDB
    success = db_client.create_document(
        document_id=doc_id,
        content=doc.content,
        embedding=embedding,
        metadata=doc.metadata
    )
    
    if success:
        return {"message": "Document created successfully", "id": doc_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to create document")

@router.get("/documents/")
async def read_documents(limit: int = 10):
    """Read all documents"""
    documents = db_client.read_documents(limit=limit)
    return {"documents": documents}

@router.get("/documents/{doc_id}")
async def read_document(doc_id: str):
    """Read a specific document"""
    documents = db_client.read_documents(ids=[doc_id])
    if documents:
        return documents[0]
    raise HTTPException(status_code=404, detail="Document not found")

@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, doc: DocumentCreate):
    """Update a document"""
    success = db_client.update_document(
        document_id=doc_id,
        content=doc.content,
        metadata=doc.metadata
    )
    
    if success:
        return {"message": "Document updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found or update failed")

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    success = db_client.delete_document(doc_id)
    
    if success:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found or delete failed")

@router.post("/query/")
async def query_documents(request: QueryRequest):
    """Query documents using vector search"""
    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(request.query)
    
    # Search in vector database
    results = db_client.query_documents(query_embedding, top_k=request.top_k)
    
    return {
        "query": request.query,
        "results": results,
        "total_matches": len(results)
    }

@router.post("/chat/")
async def chat_with_documents(request: QueryRequest):
    """Chat with documents using RAG"""
    result = rag_service.rag_query(request.query, top_k=request.top_k)
    return result

@router.post("/seed/")
async def seed_database():
    """Seed the database with sample documents"""
    seeded_ids = []
    
    for doc_data in SAMPLE_DOCUMENTS:
        doc_id = str(uuid.uuid4())
        embedding = embedding_service.generate_embedding(doc_data["content"])
        
        success = db_client.create_document(
            document_id=doc_id,
            content=doc_data["content"],
            embedding=embedding,
            metadata=doc_data["metadata"]
        )
        
        if success:
            seeded_ids.append(doc_id)
    
    return {
        "message": f"Seeded {len(seeded_ids)} documents",
        "document_ids": seeded_ids
    }

@router.get("/stats/")
async def get_database_stats():
    """Get database statistics"""
    all_ids = db_client.get_all_ids()
    return {
        "total_documents": len(all_ids),
        "document_ids": all_ids
    }