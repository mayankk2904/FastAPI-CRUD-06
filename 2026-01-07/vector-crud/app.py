from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
import ollama
import uuid

app = FastAPI()

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

# the below initialization did not work for me locally
# chroma_client = chromadb.Client(
#     chromadb.config.Settings(
#         chroma_db_impl="duckdb+parquet",
#         persist_directory="./chroma_db"
#     )
# )

collection = chroma_client.get_or_create_collection(
    name="knowledge_base"
)

DOCUMENT_TEXT = """
A database index is a data structure that improves the speed of data retrieval
operations on a database table at the cost of additional writes and storage space
to maintain the index data structure. Indexes are used to quickly locate data
without having to search every row in a database table every time said table is
accessed. Indexes can be created using one or more columns of a database table,
providing the basis for both rapid random lookups and efficient access of ordered
records.
"""

class QueryRequest(BaseModel):
    query: str

class UpdateRequest(BaseModel):
    id: str
    updated_text: str

class DeleteRequest(BaseModel):
    id: str

class ChatRequest(BaseModel):
    query: str


def generate_embedding(text: str):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]


@app.post("/create")
def create_vector():
    embedding = generate_embedding(DOCUMENT_TEXT)

    doc_id = str(uuid.uuid4())

    collection.add(
        documents=[DOCUMENT_TEXT],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[{
            "topic": "database indexing",
            "source": "manual_paragraph"
        }]
    )
    
    return {
        "message": "Document embedded and stored successfully",
        "document_id": doc_id
    }


@app.post("/read")
def read_vectors(request: QueryRequest):
    # 1. embedding for query
    query_embedding = generate_embedding(request.query)

    # 2. similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # 3. Format response
    response = []

    for i in range(len(results["documents"][0])):
        response.append({
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return {
        "query": request.query,
        "results": response
    }

@app.post("/update")
def update_vector(request: UpdateRequest):
    new_embedding = generate_embedding(request.updated_text)

    collection.upsert(
        ids=[request.id],
        documents=[request.updated_text],
        embeddings=[new_embedding],
        metadatas=[{
            "topic": "database indexing",
            "source": "updated_document"
        }]
    )

    return {
        "message": "Document updated successfully",
        "document_id": request.id
    }

@app.get("/count")
def count_vectors():
    return {
        "count": collection.count()
    }

@app.post("/delete")
def delete_vector(request: DeleteRequest):
    collection.delete(
        ids=[request.id]
    )

    return {
        "message": "Document deleted successfully",
        "document_id": request.id
    }

def generate_answer(context: str, question: str):
    prompt = f"""
Based on the context below, provide a concise answer to the question.
If the context contains relevant information that can answer the question, provide that answer.
Only say "I don't know" if the context has NO relevant information at all.

Context:
{context}

Question:
{question}

Answer (1 sentence only):
"""


    response = ollama.generate(
        model="tinyllama",
        prompt=prompt
    )

    return response["response"]

@app.post("/chat")
def chat(request: ChatRequest):
    # 1. Embed user query
    query_embedding = generate_embedding(request.query)

    # 2. Retrieve relevant docs
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # 3. Build context
    context = "\n\n".join(documents)

    # 4. Generate answer using TinyLlama
    answer = generate_answer(context, request.query)

    return {
        "query": request.query,
        "answer": answer.strip(),
        "sources": metadatas
    }

