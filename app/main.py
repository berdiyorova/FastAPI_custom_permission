from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.models.user import create_user_table

from .routers import users, auth, admins

app = FastAPI()


@app.on_event("startup")
async def startup():
    await create_user_table()



app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admins.router)


@app.get("/")
async def root():
    return RedirectResponse("/docs/")
