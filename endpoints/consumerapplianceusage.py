from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from models.product import CreateConsumerAppliancesUsage, ConsumerAppliancesUsage


router = APIRouter()


@router.get("/consumerapplianceusage/{ccm_id}")
async def get_all_appliances_by_consumer_id(
    ccm_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        statement = (
            select(ConsumerAppliancesUsage)
            .where(ConsumerAppliancesUsage.ccm_id == ccm_id)
            .order_by(ConsumerAppliancesUsage.appliance_name)
        )
        result = (await session.exec(statement)).all()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/consumerapplianceusage", status_code=201)
async def create_consumerapplianceusage(
    create_consumer_appliance_usage_data: CreateConsumerAppliancesUsage,
    session: AsyncSession = Depends(get_session),
):
    try:
        encoded_data = jsonable_encoder(create_consumer_appliance_usage_data)
        new_client = ConsumerAppliancesUsage(**encoded_data)
        session.add(new_client)
        await session.commit()
        await session.refresh(new_client)
        return new_client
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/consumerapplianceusage/{cau_id}")
async def update_consumerapplianceusage(
    cau_id: UUID,
    update_consumer_appliance_usage_data: CreateConsumerAppliancesUsage,
    session: AsyncSession = Depends(get_session),
):
    try:
        statement = select(ConsumerAppliancesUsage).where(
            ConsumerAppliancesUsage.cau_id == cau_id
        )
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        update_data = update_consumer_appliance_usage_data.model_dump(
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


@router.delete("/consumerapplianceusage/{cau_id}")
async def delete_consumer_application(
    cau_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        statement = select(ConsumerAppliancesUsage).where(
            ConsumerAppliancesUsage.cau_id == cau_id
        )
        result = (await session.exec(statement)).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        await session.delete(result)
        await session.commit()
        return

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
