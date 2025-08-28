from fastapi import FastAPI
from core.settings import get_settings
from endpoints.api import v1_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Solar", version="0.0.1")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(v1_router)
