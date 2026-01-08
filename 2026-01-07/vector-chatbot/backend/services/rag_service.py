import requests
from typing import List, Dict, Any
from database.chroma_client import ChromaClient
from services.embedding_service import EmbeddingService
from config import Config

class RAGService:
    def __init__(self):
        self.db = ChromaClient()
        self.embedding_service = EmbeddingService()
    
    def query_ollama(self, prompt: str, context: str = "") -> str:
        """Query Ollama LLM with context"""
        try:
            full_prompt = f"""Context: {context}

Question: {prompt}

Based on the context above, answer the question. If the context doesn't contain relevant information, say "I don't have enough information to answer this question"."""
            
            response = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": Config.LLM_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response from LLM")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error querying LLM: {str(e)}"
    
    def rag_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Complete RAG pipeline"""
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Retrieve similar documents
        retrieved_docs = self.db.query_documents(query_embedding, top_k=top_k)
        
        # Format context
        context = "\n\n".join([doc['content'] for doc in retrieved_docs])
        
        # Generate answer using LLM
        answer = self.query_ollama(query, context)
        
        return {
            "query": query,
            "answer": answer,
            "retrieved_documents": retrieved_docs,
            "context": context
        }