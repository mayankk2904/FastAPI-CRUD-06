import requests
import json
from typing import List
from config import Config

class EmbeddingService:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": Config.EMBEDDING_MODEL,
                    "prompt": text
                }
            )
            
            if response.status_code == 200:
                return response.json().get("embedding", [])
            else:
                print(f"Error from Ollama: {response.text}")
                # Return a dummy embedding if Ollama fails
                return [0.0] * 384  # nomic-embed-text has 384 dimensions
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 384
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embeddings.append(self.generate_embedding(text))
        return embeddings