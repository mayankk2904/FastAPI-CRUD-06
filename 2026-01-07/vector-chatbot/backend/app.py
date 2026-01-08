from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router
import uvicorn
from config import Config

app = FastAPI(title="Vector Database Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Vector Database Chatbot API",
        "endpoints": {
            "create_document": "POST /api/v1/documents/",
            "read_documents": "GET /api/v1/documents/",
            "query": "POST /api/v1/query/",
            "chat": "POST /api/v1/chat/",
            "seed": "POST /api/v1/seed/"
        }
    }

if __name__ == "__main__":
    print(f"🚀 Starting server on http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"📚 ChromaDB directory: {Config.CHROMA_PERSIST_DIRECTORY}")
    print(f"🤖 Ollama URL: {Config.OLLAMA_BASE_URL}")
    print(f"🧠 Embedding model: {Config.EMBEDDING_MODEL}")
    print(f"💬 LLM model: {Config.LLM_MODEL}")
    
    uvicorn.run("app:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)