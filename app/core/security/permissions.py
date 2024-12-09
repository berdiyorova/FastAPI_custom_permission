from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.constants import UserRole
from app.core.models.user import UserModel
from app.core.security.jwt_token import get_current_active_user



async def is_admin(user: Annotated[UserModel, Depends(get_current_active_user)]) -> UserModel:
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action, ADMIN only"
        )
    return user


async def is_user(user: Annotated[UserModel, Depends(get_current_active_user)]) -> UserModel:
    if user.role != UserRole.USER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action, USER only"
        )
    return user


async def is_admin_or_user(user: Annotated[UserModel, Depends(get_current_active_user)]) -> UserModel:
    if user.role not in [UserRole.ADMIN.value, UserRole.USER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action, ADMIN or USER only"
        )
    return user
