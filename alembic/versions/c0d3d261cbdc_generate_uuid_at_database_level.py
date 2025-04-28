"""Generate UUID at database level

Revision ID: c0d3d261cbdc
Revises: 2b901ddbd606
Create Date: 2025-04-28 16:47:37.191167

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0d3d261cbdc"
down_revision: Union[str, None] = "2b901ddbd606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    existing_tables = [
        "places",
        "places_tags",
        "tag_types",
        "tags",
    ]

    for table in existing_tables:
        op.alter_column(
            table,
            "id",
            server_default=sa.text("gen_random_uuid()"),
            existing_type=sa.dialects.postgresql.UUID(),
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
