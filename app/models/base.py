import datetime
import uuid

from pydantic import BaseModel
from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import DeclarativeBase


class Base(DeclarativeBase):
    """Base model for all database models.

    This class provides common attributes and methods for all models, including
    an ID, timestamps for creation and updates, and a method to update the model
    instance with data from a Pydantic model.

    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    def update(self, data: BaseModel) -> None:
        """Update the model instance with the provided data.

        Args:
            data (BaseModel): The data to update the model with. Must be a Pydantic model.

        """
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(self, key, value)
