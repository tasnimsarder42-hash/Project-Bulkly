from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_access_token
from app.core.config import settings
from app.models import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # In development mode, allow unauthenticated access with a mock user
    if credentials is None or not credentials.credentials:
        if settings.DEBUG:
            # Return a mock admin user for development
            mock_user = User()
            mock_user.id = "dev-admin-001"
            mock_user.email = "admin@bulkly.dev"
            mock_user.full_name = "Dev Admin"
            mock_user.role = "super_admin"
            mock_user.org_id = "dev-org-001"
            mock_user.is_active = "true"
            return mock_user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_access_token(credentials.credentials)
    user_id: str = payload.get("sub")
    if not user_id:
        if settings.DEBUG:
            mock_user = User()
            mock_user.id = "dev-admin-001"
            mock_user.email = "admin@bulkly.dev"
            mock_user.full_name = "Dev Admin"
            mock_user.role = "super_admin"
            mock_user.org_id = "dev-org-001"
            mock_user.is_active = "true"
            return mock_user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        if settings.DEBUG:
            mock_user = User()
            mock_user.id = "dev-admin-001"
            mock_user.email = "admin@bulkly.dev"
            mock_user.full_name = "Dev Admin"
            mock_user.role = "super_admin"
            mock_user.org_id = "dev-org-001"
            mock_user.is_active = "true"
            return mock_user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def require_roles(*roles: str):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(roles)}",
            )
        return current_user
    return role_checker


require_admin = require_roles("super_admin", "org_admin")
require_super_admin = require_roles("super_admin")

