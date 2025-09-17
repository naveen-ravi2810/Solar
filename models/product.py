from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from sqlalchemy import func


# ---------- Common Timestamp Mixin ----------
class TimestampMixin(SQLModel):
    created_on: datetime = Field(
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )
    updated_on: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        },
        nullable=False,
    )


# ---------- Category ----------
class Category(TimestampMixin, SQLModel, table=True):
    ctg_id: UUID = Field(primary_key=True, default_factory=uuid4)
    ctg_name: str = Field()


# ---------- Product ----------
class Product(TimestampMixin, SQLModel, table=True):
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
    requirements: List["RequirementProducts"] = Relationship(back_populates="product")
    consumer_requirement_product: List["ConsumerRequirementProduct"] = Relationship(
        back_populates="product_details"
    )


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


# ---------- Requirement ----------
class RequirementCreate(SQLModel):
    req_name: str = Field(min_length=3)


class UpdateRequirement(BaseModel):
    req_name: str = Field(min_length=3)
    req_kilo_watt: int = Field(default=2)


class Requirement(TimestampMixin, RequirementCreate, table=True):
    req_id: UUID = Field(primary_key=True, default_factory=uuid4)
    req_kilo_watt: int = Field(default=2)
    products_link: List["RequirementProducts"] = Relationship(
        back_populates="requirement"
    )


class RequirementProductsCreate(SQLModel):
    req_id: UUID = Field(foreign_key="requirement.req_id", ondelete="CASCADE")
    prod_id: UUID = Field(foreign_key="product.prd_id")
    prod_quantity: int = Field(gt=0)

    __table_args__ = (UniqueConstraint("req_id", "prod_id", name="uq_req_prod"),)


class RequirementProducts(TimestampMixin, RequirementProductsCreate, table=True):
    prd_req_id: UUID = Field(primary_key=True, default_factory=uuid4)
    product: Optional["Product"] = Relationship(back_populates="requirements")
    requirement: Optional["Requirement"] = Relationship(back_populates="products_link")


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


# ---------- Clients & Consumers ----------
class CreateClient(SQLModel):
    client_name: str
    client_phone: str = Field(min_length=9)
    client_email: str


class CreateBasicClientConsumer(SQLModel):
    client_id: UUID = Field(
        foreign_key="clients.client_id", ondelete="CASCADE", index=True
    )
    clinet_consumer_number: str
    clinet_consumer_phone_number: str
    clinet_consumer_nick_name: str


class ClientConsumerBillingType(str, Enum):
    MONTHLY = "MONTHLY"
    BI_MONTHLY = "BI_MONTHLY"


class CreateClinetConsumer(CreateBasicClientConsumer):
    clinet_consumer_meter_type: Optional[str]
    clinet_consumer_demand_load: int = Field(gt=0, default=1)
    clinet_consumed_demand_phase: int = Field(gt=0, le=3, default=1)
    client_consumer_max_consumed_units: Optional[int]
    client_consumer_avg_consumed_unit: Optional[int]
    client_consumer_peak_demand: Optional[int]
    client_consumer_avg_demand: Optional[int]
    clinet_consumer_billing_type: ClientConsumerBillingType = Field(
        default=ClientConsumerBillingType.MONTHLY,
        sa_column=SQLEnum(ClientConsumerBillingType),
    )
    clinet_consumer_requirement: str = Field(
        description="This is the core requirement of the client", default=""
    )


class ClientConsumer(TimestampMixin, CreateClinetConsumer, table=True):
    ccm_id: UUID = Field(primary_key=True, default_factory=uuid4)
    client: Optional["Clients"] = Relationship(back_populates="client_consumers")


class Clients(TimestampMixin, CreateClient, table=True):
    client_id: UUID = Field(primary_key=True, default_factory=uuid4)
    is_deleted: bool = Field(default=False)
    client_consumers: List[ClientConsumer] = Relationship(back_populates="client")


# ---------- Appliances ----------
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


class Appliances(TimestampMixin, CreateAppliances, table=True):
    appliance_id: UUID = Field(default_factory=uuid4, primary_key=True)


class CreateConsumerAppliancesUsage(SQLModel):
    appliance_name: str
    appliance_watt: float = Field(gt=0)
    appliance_quantity: int = Field(gt=0)
    appliance_day_usage: float = Field(default=0)
    appliance_night_usage: float = Field(default=0)
    exclude_for_calculation: bool = Field(default=False)
    need_battery_backup: bool = Field(default=True)
    ccm_id: UUID = Field(
        foreign_key="clientconsumer.ccm_id", ondelete="CASCADE", index=True
    )


class ConsumerAppliancesUsage(TimestampMixin, CreateConsumerAppliancesUsage, table=True):
    cau_id: UUID = Field(primary_key=True, default_factory=uuid4)


# ---------- Consumer Requirement ----------
class CreateConsumerRequirement(BaseModel):
    ccm_id: UUID
    creq_name: str = Field(min_length=4)
    req_id: UUID


class ConsumerRequirement(TimestampMixin, SQLModel, table=True):
    __tablename__ = "consumer_requirement"
    con_req_id: UUID = Field(primary_key=True, default_factory=uuid4)
    ccm_id: UUID = Field(
        foreign_key="clientconsumer.ccm_id", ondelete="CASCADE", index=True
    )
    creq_name: str
    consumer_requirement_descriptin: str = Field(default="")
    proposed_recommandation: str = Field(default="")
    consumer_requirement_products: List["ConsumerRequirementProduct"] = Relationship(
        back_populates="consumer_requirement"
    )


class ConsumerRequirementProduct(TimestampMixin, SQLModel, table=True):
    __tablename__ = "consumer_requirement_products"
    conrp_id: UUID = Field(primary_key=True, default_factory=uuid4)
    con_req_id: UUID = Field(
        foreign_key="consumer_requirement.con_req_id", ondelete="CASCADE"
    )
    prd_id: UUID = Field(foreign_key="product.prd_id", ondelete="CASCADE")
    quantity: int = Field(gt=0)
    consumer_requirement: Optional[ConsumerRequirement] = Relationship(
        back_populates="consumer_requirement_products"
    )
    product_details: Optional[Product] = Relationship(
        back_populates="consumer_requirement_product"
    )

    __table_args__ = (UniqueConstraint("con_req_id", "prd_id", name="uq_con_req_prd"),)
