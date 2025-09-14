from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class ProductBase(BaseModel):
    prd_id: UUID
    prod_name: str
    prd_capacity: int
    prd_price: float
    prd_gst: float

    class Config:
        from_attributes = True  # <-- IMPORTANT


class RequirementProductOut(BaseModel):
    prd_req_id: UUID
    prod_quantity: int
    product: ProductBase

    class Config:
        from_attributes = True  # <-- IMPORTANT


class RequirementOut(BaseModel):
    req_id: UUID
    req_name: str
    req_kilo_watt: float
    created_at: datetime
    products_link: List[RequirementProductOut]

    class Config:
        from_attributes = True  # <-- IMPORTANT
