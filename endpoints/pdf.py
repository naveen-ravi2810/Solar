# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from core.db import get_session
# from uuid import UUID

# from services.pdf import get_quotation_data, generate_pdf

# router = APIRouter()


# @router.post("/generate/{req_id}")
# async def generate_pdf_with_req_id(
#     req_id: UUID, session: AsyncSession = Depends(get_session)
# ):
#     try:
#         (
#             quotation,
#             products,
#             sub_total,
#             cgst_amount,
#             sgst_amount,
#             final_total,
#         ) = await get_quotation_data(req_id=req_id, session=session)
#         await generate_pdf(
#             quotation=quotation,
#             products=products,
#             sub_total=sub_total,
#             cgst_amount=cgst_amount,
#             sgst_amount=sgst_amount,
#             final_total=final_total,
#         )
#         return {"status": "PDF generated Successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
