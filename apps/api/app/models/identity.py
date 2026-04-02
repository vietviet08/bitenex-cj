"""Identity model for anonymous_id to user mapping."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class Identity(Base, UUIDMixin):
    """Identity mapping stored in Postgres."""

    __tablename__ = "identities"

    anonymous_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    device_id: Mapped[str | None] = mapped_column(String, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="identities",
    )

    def __repr__(self) -> str:
        return f"<Identity(anonymous_id={self.anonymous_id}, user_id={self.user_id})>"
