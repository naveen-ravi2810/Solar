from sqlmodel import SQLModel, Field, UniqueConstraint
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Category(SQLModel, table=True):
    ctg_id: UUID = Field(primary_key=True, default_factory=uuid4)
    ctg_name: str = Field()


class Product(SQLModel, table=True):
    prd_id: UUID = Field(primary_key=True, default_factory=uuid4)
    prod_name: str = Field(min_length=3)
    prd_capacity: int = Field()
    prd_price: float = Field(gt=0)
    prd_gst: float = Field(ge=0, le=100)
    ctg_id: UUID = Field(foreign_key="category.ctg_id")


class ProductRead(BaseModel):
    prd_id: UUID
    prod_name: str
    prd_capacity: int
    prd_price: float
    prd_gst: float
    ctg_id: UUID
    ctg_name: str


class RequirementCreate(SQLModel):
    req_name: str = Field(min_length=3)


class Requirement(RequirementCreate, table=True):
    req_id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)


class RequirementProductsCreate(SQLModel):
    req_id: UUID = Field(foreign_key="requirement.req_id")
    prod_id: UUID = Field(foreign_key="product.prd_id")
    prod_quantity: int = Field(gt=0)

    __table_args__ = (
        UniqueConstraint("req_id", "prod_id", name="uq_req_prod"),
    )


class RequirementProducts(RequirementProductsCreate, table=True):
    prd_req_id: UUID = Field(primary_key=True, default_factory=uuid4)



class ProductInRequirement(BaseModel):
    prd_id: UUID
    prod_name: str
    prd_capacity: int
    prd_price: float
    prd_gst: float
    prod_quantity: int
    req_name: str
    req_id: UUID
    prd_req_id: UUID
