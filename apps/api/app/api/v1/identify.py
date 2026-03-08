"""Identity resolution endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenPayload, require_operator
from app.db.postgres import get_db
from app.schemas.identity import IdentifyRequest, IdentifyResponse
from app.services.identity_service import IdentityService

router = APIRouter()


@router.post("/identify", response_model=IdentifyResponse)
async def identify(
    request: IdentifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[TokenPayload, Depends(require_operator)],
) -> IdentifyResponse:
    """
    Link anonymous_id to user identifiers.

    Creates or updates identity mapping for the given anonymous_id.
    Supports linking to user_id, email, phone, and device_id.

    Requires operator or admin role.
    """
    identity_service = IdentityService(db)
    user_id = await identity_service.identify(request)

    return IdentifyResponse(status="ok", user_id=user_id)
