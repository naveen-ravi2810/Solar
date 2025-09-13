from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from models.product import CreateConsumerAppliancesUsage, ConsumerAppliancesUsage


router = APIRouter()


# @router.get("/consumerapplianceusage/{ccm_id}")
# async def get_all_appliances_by_consumer_id(ccm_id: UUID)