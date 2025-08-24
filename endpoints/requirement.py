from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from sqlmodel import select
from models.product import Requirement, RequirementCreate, Product, RequirementProducts
from sqlalchemy import func
from uuid import UUID


router = APIRouter()

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



@router.get("/requirement")
async def get_requirements(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            Requirement.req_id,
            Requirement.req_name,
            Requirement.created_at,
            func.coalesce(
                func.sum(
                    (Product.prd_price + (Product.prd_price * (Product.prd_gst / 100)))
                    * RequirementProducts.prod_quantity
                ),
                0.0,
            ).label("total_cost"),
            func.coalesce(func.count(RequirementProducts.prod_id), 0).label(
                "total_products"
            ),
        )
        .select_from(Requirement)  # 👈 start from Requirement
        .join(
            RequirementProducts,
            Requirement.req_id == RequirementProducts.req_id,
            isouter=True,
        )  # LEFT JOIN
        .join(
            Product, Product.prd_id == RequirementProducts.prod_id, isouter=True
        )  # LEFT JOIN
        .group_by(Requirement.req_id, Requirement.req_name, Requirement.created_at).order_by(Requirement.req_name)
    )

    result = await session.execute(stmt)
    rows = result.all()
    requirements = [
        {
            "req_id": r.req_id,
            "req_name": r.req_name,
            "created_at": r.created_at,
            "total_cost": r.total_cost,
            "total_products": r.total_products,
        }
        for r in rows
    ]

    return requirements



@router.delete("/requirement/{req_id}")
async def delete_requirements(req_id: UUID, session: AsyncSession= Depends(get_session)):
    try:
        statement = select(Requirement).where(Requirement.req_id == req_id )
        instance = (await session.exec(statement=statement)).one()
        if instance:
            await session.delete(instance)
            await session.commit()
            return JSONResponse(content={
                "message": "Deleted Successfully",
            }, status_code=204)
        else:
            return HTTPException(status_code=400, detail=f"Not Found")
    except Exception as e:
        return HTTPException(status_code=400, detail=f"{str(e)}")