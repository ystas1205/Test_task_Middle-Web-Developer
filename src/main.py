import uvicorn

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from src.currency.router import (
    router_currencies,
    router_currency,
    router_update,
    router_history,
)
from src.user.auth import auth_backend
from src.user.manager import get_user_manager
from src.user.models import User
from src.user.shema import UserCreate, UserRead

app = FastAPI(title="APIcorruncy")

""" Роутер для currencies"""
app.include_router(router_currencies)
""" Роутер для currency"""
app.include_router(router_currency)
""" Роутер для обновления currency"""
app.include_router(router_update)
"""Роутер для истории валюты"""
app.include_router(router_history)

""" Настройки роутеров дял user """

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
