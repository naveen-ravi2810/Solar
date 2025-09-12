from fastapi import APIRouter
from .products import router as product_router
from .category import router as category_router
from .requirement import router as requirement_router
from .requirement_product import router as requirement_product_router
from .client import router as client_router
from .client_requirement import router as client_requirement_router
from .client_consumer import router as client_consumer_router
# from .pdf import router as pdf_router
# from .quotation import router as quotation_router


v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(category_router, tags=["Category"])
v1_router.include_router(product_router, tags=["Product"])
v1_router.include_router(requirement_router, tags=["Requirement"])
v1_router.include_router(requirement_product_router, tags=["Requirement Product"])
v1_router.include_router(client_router, tags=["Client"])
v1_router.include_router(client_requirement_router, tags=["Client Requirement Product"])
v1_router.include_router(client_consumer_router, tags=["Client Cosnumer"])
# v1_router.include_router(pdf_router, tags=["PDF generation"])
# v1_router.include_router(quotation_router, tags=["Quotation"])
