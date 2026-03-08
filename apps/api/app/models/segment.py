"""Segment model for user segmentation."""

from typing import Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Segment(Base, UUIDMixin, TimestampMixin):
    """Segment definition stored in Postgres."""

    __tablename__ = "segments"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    definition_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"<Segment(id={self.id}, name={self.name})>"
