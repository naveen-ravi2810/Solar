"""Added BILLING TYPE IN CLIENT_CONSUMER table

Revision ID: 3bb71a6981d6
Revises: 8a84cff31d8e
Create Date: 2025-09-13 22:26:28.231870

"""

from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa
from models.product import ClientConsumerBillingType


# revision identifiers, used by Alembic.
revision: str = "3bb71a6981d6"
down_revision: Union[str, Sequence[str], None] = "8a84cff31d8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type in DB
    billing_enum = sa.Enum("MONTHLY", "BI_MONTHLY", name="clientconsumerbillingtype")
    billing_enum.create(op.get_bind(), checkfirst=True)

    # Add the column with the enum
    op.add_column(
        "clientconsumer",
        sa.Column(
            "clinet_consumer_billing_type",
            billing_enum,
            nullable=False,
            server_default=ClientConsumerBillingType.MONTHLY.value,
        ),
    )


def downgrade() -> None:
    op.drop_column("clientconsumer", "clinet_consumer_billing_type")

    # Drop enum type
    sa.Enum(name="clientconsumerbillingtype").drop(op.get_bind(), checkfirst=True)
