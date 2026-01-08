import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
from config import Config

class ChromaClient:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def create_document(self, document_id: str, content: str, 
                       embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """Create/Insert operation"""
        try:
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata] if metadata else [{}],
                ids=[document_id]
            )
            return True
        except Exception as e:
            print(f"Error creating document: {e}")
            return False
    
    def read_documents(self, ids: Optional[List[str]] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """Read operation"""
        try:
            if ids:
                results = self.collection.get(ids=ids)
            else:
                results = self.collection.get(limit=limit)
            
            documents = []
            for i in range(len(results.get('ids', []))):
                documents.append({
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i],
                    'embedding': results['embeddings'][i] if results.get('embeddings') else None
                })
            return documents
        except Exception as e:
            print(f"Error reading documents: {e}")
            return []
    
    def update_document(self, document_id: str, content: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update operation - ChromaDB doesn't have direct update, so we replace"""
        try:
            # Get existing document
            existing = self.collection.get(ids=[document_id])
            if not existing['ids']:
                return False
            
            new_content = content if content else existing['documents'][0]
            new_metadata = metadata if metadata else existing['metadatas'][0]
            
            # Since ChromaDB doesn't support update, we delete and recreate
            self.collection.delete(ids=[document_id])
            
            # Re-add with updated content (keeping original embedding for simplicity)
            # In real scenario, you'd recompute embedding if content changed
            self.collection.add(
                documents=[new_content],
                embeddings=[existing['embeddings'][0]] if existing.get('embeddings') else None,
                metadatas=[new_metadata],
                ids=[document_id]
            )
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """Delete operation"""
        try:
            self.collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def query_documents(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Vector search operation"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            documents = []
            if results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    documents.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })
            return documents
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []
    
    def get_all_ids(self) -> List[str]:
        """Get all document IDs"""
        try:
            results = self.collection.get()
            return results['ids']
        except:
            return []