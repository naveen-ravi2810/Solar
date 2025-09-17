from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import SQLModel


class ConsumerRequirementRead(SQLModel):
    con_req_id: UUID
    ccm_id: UUID
    created_on: datetime
    creq_name: str
    consumer_requirement_descriptin: str
    proposed_recommandation: str
    consumer_requirement_products: List["ConsumerRequirementProductRead"] = []


class ConsumerRequirementProductRead(SQLModel):
    conrp_id: UUID
    con_req_id: UUID
    prd_id: UUID
    quantity: int
    product_details: "ProductBase"


class ProductBase(BaseModel):
    prd_id: UUID
    prod_name: str
    prd_capacity: int
    prd_price: float
    prd_gst: float


class ConsumerRequirementProductUpdate(SQLModel):
    quantity: Optional[int]


class RequirementProductCreate(SQLModel):
    prod_id: UUID
    quantity: int


class ConsumerRequirementMultipleProductCreate(SQLModel):
    con_req_id: UUID
    products: List[RequirementProductCreate] = []
