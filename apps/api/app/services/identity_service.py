"""Identity resolution service."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import Identity
from app.models.user import User
from app.schemas.identity import IdentifyRequest


class IdentityService:
    """Service for identity resolution and merging."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def identify(self, request: IdentifyRequest) -> str:
        """
        Link anonymous_id to user identifiers.
        Creates or updates identity and user records.
        Returns the resolved user_id.
        """
        now = datetime.now(timezone.utc)

        # Find existing identity by anonymous_id
        identity = await self._get_identity_by_anonymous_id(request.anonymous_id)

        if identity:
            # Update existing identity
            user_id = await self._update_identity(identity, request, now)
        else:
            # Create new identity
            user_id = await self._create_identity(request, now)

        await self.db.commit()
        return user_id

    async def _get_identity_by_anonymous_id(self, anonymous_id: str) -> Identity | None:
        """Find identity by anonymous_id."""
        stmt = select(Identity).where(Identity.anonymous_id == anonymous_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_or_create_user(
        self,
        user_id: str | None,
        email: str | None,
        phone: str | None,
        now: datetime,
    ) -> User:
        """Get existing user or create new one."""
        if user_id:
            # Try to find by user_id
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user

        # Try to find by email
        if email:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user

        # Try to find by phone
        if phone:
            stmt = select(User).where(User.phone == phone)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user

        # Create new user
        new_user = User(
            id=user_id or str(uuid4()),
            email=email,
            phone=phone,
            created_at=now,
            updated_at=now,
        )
        self.db.add(new_user)
        return new_user

    async def _update_identity(
        self,
        identity: Identity,
        request: IdentifyRequest,
        now: datetime,
    ) -> str:
        """Update existing identity with new information."""
        # Get or create user if we have identifying info
        if request.user_id or request.email or request.phone:
            user = await self._get_or_create_user(
                request.user_id,
                request.email,
                request.phone,
                now,
            )
            identity.user_id = user.id

        # Update identity fields
        if request.email:
            identity.email = request.email
        if request.phone:
            identity.phone = request.phone
        if request.device_id:
            identity.device_id = request.device_id
        identity.last_seen_at = now

        return identity.user_id or str(uuid4())

    async def _create_identity(
        self,
        request: IdentifyRequest,
        now: datetime,
    ) -> str:
        """Create new identity record."""
        user_id = None

        # Get or create user if we have identifying info
        if request.user_id or request.email or request.phone:
            user = await self._get_or_create_user(
                request.user_id,
                request.email,
                request.phone,
                now,
            )
            user_id = user.id

        identity = Identity(
            anonymous_id=request.anonymous_id,
            user_id=user_id,
            email=request.email,
            phone=request.phone,
            device_id=request.device_id,
            first_seen_at=now,
            last_seen_at=now,
        )
        self.db.add(identity)

        return user_id or str(uuid4())

    async def get_user_id_by_anonymous_id(self, anonymous_id: str) -> str | None:
        """Get user_id for an anonymous_id."""
        identity = await self._get_identity_by_anonymous_id(anonymous_id)
        return identity.user_id if identity else None
