"""Enable fuzzy-matching

Revision ID: 8fb30e03d16b
Revises: c618f5880466
Create Date: 2025-04-18 15:45:57.743421

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8fb30e03d16b"
down_revision: Union[str, None] = "c618f5880466"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        "idx_places_address_trgm",
        "places",
        ["address"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"address": "gin_trgm_ops"},
    )
    op.create_index(
        "idx_places_name_trgm",
        "places",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_index(
        "idx_places_name_zh_trgm",
        "places",
        ["name_zh"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name_zh": "gin_trgm_ops"},
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_places_name_zh_trgm",
        table_name="places",
        postgresql_using="gin",
        postgresql_ops={"name_zh": "gin_trgm_ops"},
    )
    op.drop_index(
        "idx_places_name_trgm",
        table_name="places",
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.drop_index(
        "idx_places_address_trgm",
        table_name="places",
        postgresql_using="gin",
        postgresql_ops={"address": "gin_trgm_ops"},
    )
