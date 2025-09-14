from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy.dialects.postgresql import JSONB

class ClientWithConsumers(SQLModel, table=False):  # table=False because it’s a view
    client_id: str
    client_name: str
    client_phone: str
    client_email: str
    created_on: str
    client_consumers: Optional[JSONB]  # JSONB from the view

    model_config = {
        "arbitrary_types_allowed": True  # Needed for JSONB
    }