from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from app.core.database import SessionDep
from app.core.models.user import UserModel
from app.core.security.jwt_token import get_current_active_user
from app.core.security.permissions import is_user
from app.schemas.user import UserIn

router = APIRouter(
    tags=["user"]
)


@router.get("/users/me/", response_model=UserModel, dependencies=[Depends(is_user)])
async def read_users_me(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    return current_user



@router.put("/users/me/", status_code=200, dependencies=[Depends(is_user)])
async def update_user(user_in: UserIn, session: SessionDep) -> dict:
    user = await read_users_me()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_in.username
    user.first_name = user_in.first_name
    user.last_name = user_in.last_name
    user.age = user_in.age

    session.commit()
    return user
