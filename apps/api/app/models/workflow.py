"""Workflow model for n8n automation."""

from typing import Any

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Workflow(Base, UUIDMixin, TimestampMixin):
    """Workflow configuration stored in Postgres."""

    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # abandoned_cart, onboarding, churn_warning
    n8n_workflow_id: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name}, type={self.type})>"
