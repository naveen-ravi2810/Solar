from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from schema.CosnumerRequirementProduct import ConsumerRequirementProductUpdate, ConsumerRequirementMultipleProductCreate
from models.product import ConsumerRequirementProduct

router = APIRouter()


@router.patch("/consumer_requirement_product/{conrp_id}")
async def update_consumer_requirement_product(
    conrp_id: UUID,
    consumer_requirement_product_update_data: ConsumerRequirementProductUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(ConsumerRequirementProduct).where(
            ConsumerRequirementProduct.conrp_id == conrp_id
        )
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = consumer_requirement_product_update_data.model_dump(
            exclude_unset=True
        )  # only update provided fields
        for key, value in update_data.items():
            setattr(result, key, value)
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/consumer_requirement_product/{conrp_id}")
async def delete_consumer_requirement_product(conrp_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(ConsumerRequirementProduct).where(
            ConsumerRequirementProduct.conrp_id == conrp_id
        )
        instance = (await session.exec(statement=statement)).one()
        if instance:
            await session.delete(instance)
            await session.commit()
            return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/consumer_requirement_product")
async def add_products_to_requirement(
    payload: ConsumerRequirementMultipleProductCreate, session: AsyncSession = Depends(get_session)
):
    con_req_id = payload.con_req_id
    products = payload.products 

    for prod in products:
        new_item = ConsumerRequirementProduct(
            con_req_id=con_req_id,
            prd_id=prod.prod_id,
            quantity=prod.quantity
        )
        session.add(new_item)

    await session.commit()
    return {"status": "success", "added": len(products)}
