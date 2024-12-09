from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select

from app.core.database import SessionDep
from app.core.models.user import UserModel
from app.core.security.auth import validate_email_address, validate_password, check_user, get_password_hash
from app.core.security.permissions import is_admin
from app.schemas.user import UserOut, UserIn, StandardResponse

router = APIRouter(
    tags=["admin"]
)



@router.get("/users/", status_code=200, dependencies=[Depends(is_admin)])
async def get_users(page: str, page_size: str, session: SessionDep) -> list[UserOut]:
    skip = int(page) * int(page_size)
    users = session.exec(select(UserModel).offset(skip).limit(int(page_size))).all()
    return users


@router.post('/users/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(is_admin)])
async def add_user(user_in: UserIn, session: SessionDep) -> UserOut:
    await validate_email_address(email=user_in.email)
    await validate_password(password=user_in.password, confirm_password=user_in.confirm_password)
    await check_user(username=user_in.username, email=user_in.email, session=session)

    user_dict = user_in.dict()
    user_dict.pop("confirm_password")
    user_dict["password"] = await get_password_hash(user_in.password)

    user = UserModel(**user_dict)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user



@router.delete("/users/{user_id}/", status_code=200, dependencies=[Depends(is_admin)])
async def delete_user(user_id: int, session: SessionDep):
    user = session.exec(select(UserModel).where(UserModel.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return StandardResponse(success=True, message="User is successfully deleted")
