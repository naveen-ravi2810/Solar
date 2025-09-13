from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import SQLModel


class ClientConsumerRead(SQLModel):
    ccm_id: Optional[UUID]
    clinet_consumer_meter_type: Optional[str]
    clinet_consumer_demand_load: Optional[int]
    clinet_consumed_demand_phase: Optional[int]
    client_consumer_max_consumed_units: Optional[int]
    client_consumer_avg_consumed_unit: Optional[int]
    client_consumer_peak_demand: Optional[int]
    client_consumer_avg_demand: Optional[int]
    clinet_consumer_number: Optional[str]
    clinet_consumer_phone_number: Optional[str]
    clinet_consumer_nick_name: Optional[str]


class ClientConsumerUpdate(SQLModel):
    clinet_consumer_meter_type: Optional[str] = None
    clinet_consumer_demand_load: Optional[int] = None
    clinet_consumed_demand_phase: Optional[int] = None
    client_consumer_max_consumed_units: Optional[int] = None
    client_consumer_avg_consumed_unit: Optional[int] = None
    client_consumer_peak_demand: Optional[int] = None
    client_consumer_avg_demand: Optional[int] = None
    clinet_consumer_number: Optional[str] = None
    clinet_consumer_phone_number: Optional[str] = None
    clinet_consumer_nick_name: Optional[str] = None


class ClientRead(SQLModel):
    client_id: UUID
    client_name: str
    client_phone: str
    client_email: str
    created_on: datetime

    client_consumers: List[ClientConsumerRead] = []
