from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from uuid import UUID
from models.product import (
    Clients,
    CreateClient,
    ConsumerAppliancesUsage,
    ClientConsumer,
)
from sqlmodel import select, text
from sqlalchemy.orm import joinedload
from schema.clinet import ClientRead



router = APIRouter()


@router.get("/clients")
async def get_clients(session: AsyncSession = Depends(get_session)):
    try:
        statement = (
            select(Clients)
            .where(Clients.is_deleted == False)
            .order_by(Clients.client_name)
        )
        return (await session.exec(statement)).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/client/{client_id}")
async def get_clients(client_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        # Use parameterized query to avoid SQL injection
        query = text("SELECT * FROM client_with_consumers WHERE client_id = :client_id")
        result = await session.execute(query, {"client_id": str(client_id)})
        client_data = (
            result.mappings().first()
        )  # Get the first row as a dict-like object

        if not client_data:
            raise HTTPException(status_code=404, detail="Client not found")

        return client_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/client")
async def create_client(
    create_client_data: CreateClient, session: AsyncSession = Depends(get_session)
):
    try:
        encoded_data = jsonable_encoder(create_client_data)
        new_client = Clients(**encoded_data)
        session.add(new_client)
        await session.commit()
        await session.refresh(new_client)
        return new_client
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/client/{client_id}")
async def update_client(
    client_id: UUID,
    update_client_data: CreateClient,
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(Clients).where(Clients.client_id == client_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        update_data = update_client_data.model_dump(
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


@router.delete("/client/{client_id}")
async def delete_client(client_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Clients).where(Clients.client_id == client_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        result.is_deleted = True
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
