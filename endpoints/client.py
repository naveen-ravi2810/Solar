from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from uuid import UUID
from models.product import Clients, CreateClient
from sqlmodel import select
from sqlalchemy.orm import joinedload
from schema.clinet import ClientRead


router = APIRouter()


@router.get("/clients")
async def get_clients(session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Clients)
        return (await session.exec(statement)).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/client/{client_id}", response_model=ClientRead)
async def get_clients(client_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        statement = (
            select(Clients)
            .where(Clients.client_id == client_id)
            .options(joinedload(Clients.client_consumers))
        )
        return (await session.exec(statement)).unique().one()
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
