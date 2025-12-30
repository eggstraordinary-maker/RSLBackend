import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, users
from app.config import settings
from app.database import engine
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц при старте
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Жестовый помощник API",
    description="API для приложения распознавания жестов русского жестового языка",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Жестовый помощник API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)