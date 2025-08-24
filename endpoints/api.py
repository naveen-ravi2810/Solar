from fastapi import APIRouter
from .products import router as product_router
from .category import router as category_router
from  .requirement import router as requirement_router
from  .requirement_product import router as requirement_product_router


v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(category_router, tags=["Category"])
v1_router.include_router(product_router, tags=["Product"])
v1_router.include_router(requirement_router, tags=["Requirement"])
v1_router.include_router(requirement_product_router, tags=["Requirement Product"])

