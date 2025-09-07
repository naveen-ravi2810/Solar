from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from models.product import (
    Category,
    Product,
    ProductRead,
    ProductCreate
)
from fastapi.encoders import jsonable_encoder
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

@router.post("/product", response_model=ProductRead)
async def create_product(create_product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    try:
        encoded_data = jsonable_encoder(create_product_data)
        new_product = Product(**encoded_data)
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.patch("/product/{prd_id}")
async def update_product(
    prd_id: UUID,
    update_product_data: ProductCreate,   # or better: a ProductUpdate schema
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(Product).where(Product.prd_id == prd_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = update_product_data.model_dump(exclude_unset=True)  # only update provided fields
        for key, value in update_data.items():
            setattr(result, key, value)
        session.add(result)
        await session.commit()
        await session.refresh(result)

        return result

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Delete of the Product Should not happen for now
# @router.delete("/product/{prd_id}")
# async def delete_product():
#     pass