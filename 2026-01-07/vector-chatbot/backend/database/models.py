from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    created_at: str = datetime.now().isoformat()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class DocumentCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = {}