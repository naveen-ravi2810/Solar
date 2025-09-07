from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from sqlmodel import select
from models.product import Product, ProductInRequirement, Requirement, RequirementProducts, RequirementProductsCreate, UpdateProductRequirement
from typing import List
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError



router = APIRouter()

@router.get(
    "/requirementproducts/{req_id}", response_model=List[ProductInRequirement]
)
async def get_products_by_req_id(
    req_id: UUID, session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(
            Product.prd_id,
            Product.prod_name,
            Product.prd_capacity,
            Product.prd_price,
            Product.prd_gst,
            RequirementProducts.prod_quantity,
            Requirement.req_name,
            RequirementProducts.req_id,
            RequirementProducts.prd_req_id
        )
        .join(Product, Product.prd_id == RequirementProducts.prod_id)
        .join(Requirement, Requirement.req_id == RequirementProducts.req_id)
        .where(RequirementProducts.req_id == req_id)
    )

    result = await session.execute(stmt)
    rows = result.all()
    return rows



@router.post("/requirementproducts")
async def create_product_in_the_requirement_product_table(
    req: RequirementProductsCreate, session: AsyncSession = Depends(get_session)
):
    try:
        # Check if entry already exists
        statement = (
            select(RequirementProducts)
            .where(RequirementProducts.req_id == req.req_id)
            .where(RequirementProducts.prod_id == req.prod_id)
        )
        existance = (await session.exec(statement)).one_or_none()

        if existance:
            # Update quantity if entry exists
            existance.prod_quantity += req.prod_quantity
            session.add(existance)
            await session.commit()
            await session.refresh(existance)
            return existance
        else:
            # Create new entry if not exists
            encoded_json = jsonable_encoder(req)
            requirement_product = RequirementProducts(**encoded_json)
            session.add(requirement_product)
            await session.commit()
            await session.refresh(requirement_product)
            return requirement_product

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/requirementproducts/{req_prd_id}")
async def deleteRequirementProductById(req_prd_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        print(req_prd_id)
        statement = select(RequirementProducts).where(RequirementProducts.prd_req_id == req_prd_id)
        instance = (await session.exec(statement=statement)).one()
        print(instance.prd_req_id)
        if instance:
            await session.delete(instance)
            await session.commit()
            return 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/requirementproducts")
async def update_product_requirement(
    update_data: UpdateProductRequirement,
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await session.execute(
            select(RequirementProducts).where(
                RequirementProducts.prd_req_id == update_data.prd_req_id
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        product.prod_quantity = update_data.prod_quantity
        await session.commit()
        await session.refresh(product)

        return {"status": "success", "data": product}

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))