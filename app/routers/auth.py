from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import SessionDep
from app.core.models.user import UserModel, BlockedToken
from app.core.security.auth import get_password_hash, validate_password, check_user, validate_email_address, \
    get_user_by_username, verify_password, authenticate_user
from app.core.security.jwt_token import create_access_token
from app.schemas.user import UserIn, UserOut, Login, TokenData, Logout, StandardResponse

router = APIRouter(
    tags=["Authentication"]
)


@router.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(user_in: UserIn, session: SessionDep) -> UserOut:
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


@router.post('/login/')
async def login(data: Login, session: SessionDep) -> TokenData:
    user = await get_user_by_username(username=data.username, session=session)
    if not user or not await verify_password(plain_password=data.password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is incorrect"
        )
    access_token = await create_access_token(data={"sub": user.username})
    return TokenData(access_token=access_token, token_type="bearer")


# @router.post("/token")
# async def login_for_access_token(
#         form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#         session: SessionDep
# ) -> TokenData:
#     user = await authenticate_user(
#         username=form_data.username,
#         password=form_data.password,
#         session=session)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = await create_access_token(data={"sub": user.username})
#     return TokenData(access_token=access_token, token_type="bearer")


@router.post('/logout/')
async def logout(token: Logout, session: SessionDep) -> StandardResponse:
    blocked_token = BlockedToken(token=token.access_token)
    session.add(blocked_token)
    session.commit()
    session.refresh(blocked_token)
    return StandardResponse(success=True, message="Successfully logged out")
