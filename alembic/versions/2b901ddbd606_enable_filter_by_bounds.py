"""Enable filter by bounds

Revision ID: 2b901ddbd606
Revises: 8fb30e03d16b
Create Date: 2025-04-18 20:29:07.857742

"""

from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b901ddbd606"
down_revision: Union[str, None] = "8fb30e03d16b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.add_column(
        "places",
        sa.Column(
            "location_geom",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE places SET location_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)"
    )
    op.create_index(
        "idx_places_location_geom",
        "places",
        ["location_geom"],
        unique=False,
        postgresql_using="gist",
        if_not_exists=True,
    )

    op.drop_column("places", "longitude")
    op.drop_column("places", "latitude")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "places",
        sa.Column(
            "latitude",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "places",
        sa.Column(
            "longitude",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE places SET latitude = ST_Y(location_geom), longitude = ST_X(location_geom)"
    )

    op.drop_index(
        "idx_places_location_geom", table_name="places", postgresql_using="gist"
    )
    op.drop_column("places", "location_geom")

    op.execute("DROP EXTENSION IF EXISTS postgis")
