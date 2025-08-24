from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from sqlmodel import select
from models.product import Category

router = APIRouter()


@router.get("/category")
async def get_category(session: AsyncSession = Depends(get_session)):
    statement = select(Category)
    return (await session.exec(statement=statement)).all()
