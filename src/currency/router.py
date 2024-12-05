from fastapi import Query
from fastapi_users import FastAPIUsers
from src.user.manager import get_user_manager
from src.user.models import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as As
from src.database import get_async_session
from src.models.models import Currency
from sqlalchemy.exc import SQLAlchemyError
from src.user.auth import auth_backend
import requests
import xml.etree.ElementTree as ET
from sqlalchemy import delete, text

router_currencies = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)

router_currency = APIRouter(
    prefix="/currency",
    tags=["Currency"]
)

router_update = APIRouter(
    prefix="/api/update",
    tags=["Update_currency"]
)

""" Зависимости для авторизации"""
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
current_active_user = fastapi_users.current_user(active=True)


@router_currencies.get("/")
async def get_list_exchange_rates(skip: int = Query(0), limit: int = Query(10),
                                  session: As = Depends(get_async_session),
                                  user: User = Depends(current_active_user)):
    """ Возвращает список курсов валют с возможность пагинации"""
    try:
        query = select(Currency).offset(skip).limit(limit)
        result = await session.execute(query)
        currency = result.scalars().all()
        return currency
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail={"error": "Ошибка базы данных"})


@router_currency.get("/")
async def get_currensy_by_id(currency_id: int,
                             session: As = Depends(get_async_session)):
    """ Возвращает курс валюты для переданного id  """
    try:
        currency = await session.get(Currency, currency_id)
        if not currency:
            raise HTTPException(status_code=404, detail="Элемент не найден")
        return currency
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail={"error": "Ошибка базы данных"})


@router_update.get("/")
async def history_of_exchange_rates(session: As = Depends(get_async_session)):
    """ Обноляет курс валют"""
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    response = requests.get(url)
    root = ET.fromstring(response.content)
    # удаляем все старые записи из таблицы
    await session.execute(delete(Currency))
    # Сброс последовательности идентификатора для таблицы Currency
    await session.execute(
        text("ALTER SEQUENCE currency_id_seq RESTART WITH 1"))

    for valute in root.findall('.//Valute'):
        new_currency = Currency(name=valute.find('Name').text,
                                rate=valute.find('Value').text)
        session.add(new_currency)
    await session.commit()
    return {"Курсы валют обновлены"}
