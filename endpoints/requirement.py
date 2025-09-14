from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from sqlmodel import select
from models.product import (
    Requirement,
    RequirementCreate,
    Product,
    RequirementProducts,
    UpdateRequirement,
)
from sqlalchemy import func, cast, Numeric
from uuid import UUID


router = APIRouter()


TOTAL_COST_EXPR = func.coalesce(
    func.round(
        cast(
            func.sum(
                (Product.prd_price + (Product.prd_price * (Product.prd_gst / 100)))
                * RequirementProducts.prod_quantity
            ),
            Numeric(12, 2),  # cast to numeric for PostgreSQL rounding
        ),
        2,
    ),
    0.0,
).label("total_cost")

TOTAL_RPODUCTS_EXPERSSION = func.coalesce(
    func.sum(RequirementProducts.prod_quantity), 0
).label("total_products")


@router.post("/requirement", response_model=Requirement)
async def create_requirement(
    req_data: RequirementCreate, session: AsyncSession = Depends(get_session)
):
    try:
        encoded_json = jsonable_encoder(req_data)
        requirement = Requirement(**encoded_json)
        session.add(requirement)
        await session.commit()
        await session.refresh(requirement)
        return requirement
    except Exception as e:
        return HTTPException(status_code=400, detail=f"{str(e)}")


@router.get("/requirement/{req_id}")
async def get_requirement_details_by_id(
    req_id: UUID, session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(
            Requirement.req_id,
            Requirement.req_name,
            Requirement.created_at,
            Requirement.req_kilo_watt,
            TOTAL_COST_EXPR,
            TOTAL_RPODUCTS_EXPERSSION,
        )
        .select_from(Requirement)
        .join(
            RequirementProducts,
            Requirement.req_id == RequirementProducts.req_id,
            isouter=True,
        )
        .join(Product, Product.prd_id == RequirementProducts.prod_id, isouter=True)
        .group_by(
            Requirement.req_id,
            Requirement.req_name,
            Requirement.created_at,
            Requirement.req_kilo_watt,
        )
        .order_by(Requirement.req_name)
        .where(Requirement.req_id == req_id)
    )

    result = await session.execute(stmt)
    rows = result.one_or_none()
    if rows:
        return {
            "req_id": rows.req_id,
            "req_name": rows.req_name,
            "created_at": rows.created_at,
            "total_cost": rows.total_cost,
            "total_products": rows.total_products,
            "req_kilo_watt": rows.req_kilo_watt,
        }
    else:
        raise HTTPException(status_code=400, detail="Data not found")


@router.get("/requirement")
async def get_requirements(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            Requirement.req_id,
            Requirement.req_name,
            Requirement.created_at,
            Requirement.req_kilo_watt,
            TOTAL_COST_EXPR,
            TOTAL_RPODUCTS_EXPERSSION,
        )
        .select_from(Requirement)
        .join(
            RequirementProducts,
            Requirement.req_id == RequirementProducts.req_id,
            isouter=True,
        )
        .join(Product, Product.prd_id == RequirementProducts.prod_id, isouter=True)
        .group_by(
            Requirement.req_id,
            Requirement.req_name,
            Requirement.created_at,
            Requirement.req_kilo_watt,
        )
        .order_by(Requirement.req_name)
    )

    result = await session.execute(stmt)
    rows = result.all()

    requirements = [
        {
            "req_id": r.req_id,
            "req_name": r.req_name,
            "created_at": r.created_at,
            "total_cost": float(r.total_cost),  # convert Numeric -> float
            "total_products": r.total_products,
            "req_kilo_watt": r.req_kilo_watt,
        }
        for r in rows
    ]

    return requirements


@router.delete("/requirement/{req_id}")
async def delete_requirements(
    req_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        statement = select(Requirement).where(Requirement.req_id == req_id)
        instance = (await session.exec(statement=statement)).one()
        if instance:
            await session.delete(instance)
            await session.commit()
            return JSONResponse(
                content={
                    "message": "Deleted Successfully",
                },
                status_code=204,
            )
        else:
            return HTTPException(status_code=400, detail=f"Not Found")
    except Exception as e:
        return HTTPException(status_code=400, detail=f"{str(e)}")


@router.patch("/requirement/{req_id}")
async def update_requirement(
    req_id: UUID,
    update_requirement_data: UpdateRequirement,
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(Requirement).where(Requirement.req_id == req_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = update_requirement_data.model_dump(
            exclude_unset=True
        )  # only update provided fields
        for key, value in update_data.items():
            setattr(result, key, value)
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
