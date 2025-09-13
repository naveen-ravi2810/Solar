from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from models.product import Appliances, CreateAppliances

router = APIRouter()

@router.get("/appliances")
async def ge_all_appliances(session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Appliances).order_by(Appliances.appliance_name)
        result =  (await session.exec(statement)).all()
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/appliances")
async def create_appliances(create_new_appliance: CreateAppliances, session: AsyncSession = Depends(get_session)):
    try:
        new_appliance = Appliances(
            **jsonable_encoder(create_new_appliance)
        )
        session.add(new_appliance)
        await session.commit()
        await session.refresh(new_appliance)
        return new_appliance
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/appliances/{appliance_id}")
async def update_appliance_by_id(appliance_id:UUID,create_new_appliance:CreateAppliances,  session:AsyncSession =Depends(get_session)):
    try:
        statement = select(Appliances).where(Appliances.appliance_id == appliance_id)
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = create_new_appliance.model_dump(
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
    

@router.delete("/appliances/{appliance_id}")
async def delete_client_consumer_by_id(
    appliance_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        statement = select(Appliances).where(Appliances.appliance_id == appliance_id)
        instance = (await session.exec(statement=statement)).one()
        if instance:
            await session.delete(instance)
            await session.commit()
            return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
