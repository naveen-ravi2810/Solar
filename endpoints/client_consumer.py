from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from models.product import (
    CreateBasicClientConsumer,
    ClientConsumer,
)
from models.product import ClientConsumer
from schema.clinet import ClientConsumerRead, ClientConsumerUpdate

router = APIRouter()


@router.post("/client_consumer")
async def create_client_consumer(
    create_client_consumer: CreateBasicClientConsumer,
    session: AsyncSession = Depends(get_session),
):
    try:
        new_client_consumer_basic_details = ClientConsumer(
            **jsonable_encoder(create_client_consumer)
        )
        session.add(new_client_consumer_basic_details)
        await session.commit()
        await session.refresh(new_client_consumer_basic_details)
        return new_client_consumer_basic_details
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clinet_consumer/{ccm_id}")
async def delete_client_consumer_by_id(
    ccm_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        statement = select(ClientConsumer).where(ClientConsumer.ccm_id == ccm_id)
        instance = (await session.exec(statement=statement)).one()
        if instance:
            await session.delete(instance)
            await session.commit()
            return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/clinet_consumer/{ccm_id}")
async def update_product(
    ccm_id: UUID,
    update_clinet_consumer_data: ClientConsumerUpdate,  # or better: a ProductUpdate schema
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(ClientConsumer).where(ClientConsumer.ccm_id == ccm_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = update_clinet_consumer_data.model_dump(
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
