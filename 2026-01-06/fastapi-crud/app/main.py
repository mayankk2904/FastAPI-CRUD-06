from fastapi import FastAPI
from app.routers.users import router as user_router

app = FastAPI(title="User Management API using FastAPI and MongoDB")

app.include_router(user_router)
