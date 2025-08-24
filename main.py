from fastapi import FastAPI
from core.settings import get_settings
from endpoints.api import v1_router


app = FastAPI(title="Solar", version="0.0.1")


app.include_router(v1_router)
