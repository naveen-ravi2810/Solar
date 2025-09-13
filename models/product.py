from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Enum as SQLEnum  # SQLAlchemy Enum
from enum import Enum


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
    description: str = Field(default="Kindly add description")
    show_prd_product: bool = Field(default=True)
    show_prd_price: bool = Field(default=True)
    show_prd_quantity: bool = Field(default=True)


class ProductCreate(BaseModel):
    prod_name: str = Field(min_length=3)
    prd_capacity: int = Field()
    prd_price: float = Field(gt=0)
    prd_gst: float = Field(ge=0, le=100)
    ctg_id: UUID
    show_prd_product: bool = Field(default=True)
    show_prd_price: bool = Field(default=True)
    show_prd_quantity: bool = Field(default=True)


class ProductRead(BaseModel):
    prd_id: UUID
    prod_name: str
    prd_capacity: int
    prd_price: float
    prd_gst: float
    ctg_id: UUID
    ctg_name: str
    description: str
    show_prd_price: bool
    show_prd_product: bool
    show_prd_quantity: bool


class RequirementCreate(SQLModel):
    req_name: str = Field(min_length=3)


class Requirement(RequirementCreate, table=True):
    req_id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)


class RequirementProductsCreate(SQLModel):
    req_id: UUID = Field(foreign_key="requirement.req_id", ondelete="CASCADE")
    prod_id: UUID = Field(foreign_key="product.prd_id")
    prod_quantity: int = Field(gt=0)

    __table_args__ = (UniqueConstraint("req_id", "prod_id", name="uq_req_prod"),)


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


class UpdateProductRequirement(BaseModel):
    prd_req_id: UUID
    prod_quantity: int


class CreateClient(SQLModel):
    # Add latitude and longitude and fetch address
    client_name: str
    client_phone: str = Field(min_length=9)
    client_email: str


class CreateBasicClientConsumer(SQLModel):
    client_id: UUID = Field(foreign_key="clients.client_id", ondelete="CASCADE")
    clinet_consumer_number: str
    clinet_consumer_phone_number: str
    clinet_consumer_nick_name: str


class CreateClinetConsumer(CreateBasicClientConsumer):
    clinet_consumer_meter_type: Optional[str]  # mabe the choices
    clinet_consumer_demand_load: int = Field(gt=0, default=1)
    clinet_consumed_demand_phase: int = Field(
        gt=0, le=3, default=1
    )  # make dropdown 1 or 3 in frontend
    client_consumer_max_consumed_units: Optional[int]
    client_consumer_avg_consumed_unit: Optional[int]
    client_consumer_peak_demand: Optional[int]
    client_consumer_avg_demand: Optional[int]


class ClientConsumer(CreateClinetConsumer, table=True):
    ccm_id: UUID = Field(primary_key=True, default_factory=uuid4)
    client: Optional["Clients"] = Relationship(back_populates="client_consumers")


class Clients(CreateClient, table=True):
    client_id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_on: datetime = Field(default_factory=datetime.now)
    client_consumers: List[ClientConsumer] = Relationship(back_populates="client")


class ApplianceLoadType(str, Enum):
    LIGHT = "LIGHT"
    HEAVY = "HEAVY"
    INDUCTION = "INDUCTION"


class CreateAppliances(SQLModel):
    appliance_name: str
    appliance_volt: float = Field(gt=0)
    appliance_load_type: ApplianceLoadType = Field(
        default=ApplianceLoadType.LIGHT, sa_column=SQLEnum(ApplianceLoadType)
    )


class Appliances(CreateAppliances, table=True):
    appliance_id: UUID = Field(default_factory=uuid4, primary_key=True)

class CreateConsumerAppliancesUsage(SQLModel):
    appliance_name: str
    appliance_watt: float = Field(gt=0)
    appliance_quantity: int = Field(gt=0)
    appliance_day_usage: float = Field(default=0)
    appliance_night_usage: float = Field(default=0)
    exclude_for_calculation: bool = Field(default=False)
    ccm_id: UUID = Field(foreign_key="clientconsumer.ccm_id", ondelete="CASCADE")

class ConsumerAppliancesUsage(CreateConsumerAppliancesUsage, table=True):
    cau_id: UUID = Field(primary_key=True, default_factory=uuid4)

class ClientRequirement(SQLModel, table=True):
    __tablename__ = "client_requirement"
    creq_id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_on: datetime = Field(default_factory=datetime.now)
    client_id: UUID = Field(foreign_key="clients.client_id", ondelete="CASCADE")
    creq_name: str


class ClientRequirementProducts(SQLModel, table=True):
    __tablename__ = "client_requirement_products"
    crp_id: UUID = Field(primary_key=True, default_factory=uuid4)
    creq_id: UUID = Field(foreign_key="client_requirement.creq_id", ondelete="CASCADE")
    prd_id: UUID = Field(foreign_key="product.prd_id", ondelete="CASCADE")
    quantity: int = Field(gt=0)
    description: str


class CreateClientRequirement(BaseModel):
    client_id: UUID
    creq_name: str = Field(min_length=4)
    req_id: UUID
