# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy.ext.asyncio import AsyncSession
# from core.db import get_session
# from models.product import CreateQuotation, Quotation
# from uuid import UUID
# from sqlmodel import select


# router = APIRouter()


# @router.post("/quotation")
# async def create_quotation(
#     create_quotation_data: CreateQuotation, session: AsyncSession = Depends(get_session)
# ):
#     try:
#         encoded_json = jsonable_encoder(create_quotation_data)
#         new_quotation = Quotation(**encoded_json)
#         session.add(new_quotation)
#         await session.commit()
#         await session.refresh(new_quotation)
#         return new_quotation
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/quotation/{req_id}")
# async def get_quotation_by_requirement_id(
#     req_id: UUID, session: AsyncSession = Depends(get_session)
# ):
#     try:
#         statement = select(Quotation).where(Quotation.req_id == req_id)
#         result = (await session.execute(statement=statement)).one_or_none()
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
