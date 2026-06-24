import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import UserOut, UserInviteRequest
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserOut])
async def get_org_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all users in the current user's organization."""
    result = await db.execute(select(User).where(User.org_id == current_user.org_id))
    return result.scalars().all()

@router.post("/invite", response_model=UserOut)
async def invite_user(
    payload: UserInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a new user to the organization (simulated)."""
    # Check if user exists
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create pending user
    new_user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        full_name="Pending Invite",
        hashed_password=get_password_hash("temporary_password_123!"), # In a real app, generate token and send email
        role=payload.role,
        org_id=current_user.org_id,
        is_active=False,  # pending
        is_verified=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
