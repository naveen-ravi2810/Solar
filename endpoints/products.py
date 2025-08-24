from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from models.product import (
    Category,
    Product,
    ProductRead,
)
from sqlmodel import select
from uuid import UUID
from typing import List


router = APIRouter()



@router.get("/product/{ctg_id}")
async def get_products_by_category_id(
    ctg_id: UUID, session: AsyncSession = Depends(get_session)
):
    statement = select(Product).where(Product.ctg_id == ctg_id)
    return (await session.exec(statement=statement)).all()


@router.get("/product", response_model=List[ProductRead])
async def get_product(session: AsyncSession = Depends(get_session)):
    statement = (
        select(
            Product.prd_id,
            Product.prod_name,
            Product.prd_capacity,
            Product.prd_price,
            Product.prd_gst,
            Product.ctg_id,
            Category.ctg_name,
        )
        .select_from(Product)
        .join(Category, Category.ctg_id == Product.ctg_id)
        .order_by(Product.prod_name)
    )
    a = (await session.exec(statement=statement)).all()

    return a
