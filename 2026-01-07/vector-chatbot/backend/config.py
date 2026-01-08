import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY = "./chroma_db"
    CHROMA_COLLECTION_NAME = "documents_collection"
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    EMBEDDING_MODEL = "nomic-embed-text"  # Lightweight embedding model
    LLM_MODEL = "llama2"  # or "mistral", "gemma" based on what you have
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000