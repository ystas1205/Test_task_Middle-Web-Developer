from fastapi import Query
from fastapi_users import FastAPIUsers
from src.user.manager import get_user_manager
from src.user.models import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as As
from src.database import get_async_session
from src.models.models import Currency, History_Currency
from sqlalchemy.exc import SQLAlchemyError
from src.user.auth import auth_backend
import requests
import xml.etree.ElementTree as ET
from sqlalchemy import delete, text
from typing import Optional
from datetime import date

router_currencies = APIRouter(
    prefix="/api/currencies",
    tags=["Currencies"]
)

router_currency = APIRouter(
    prefix="/api/currency",
    tags=["Currency"]
)

router_update = APIRouter(
    prefix="/api/update",
    tags=["Update_currency"]
)

router_history = APIRouter(
    prefix="/api/history",
    tags=["History_currency"]

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
        new_currency_history = History_Currency(name=valute.find('Name').text,
                                                rate=valute.find('Value').text
                                                )

        session.add(new_currency)
        session.add(new_currency_history)
    await session.commit()
    return {"message": "Курсы валют обновлены"}


@router_history.get("/")
async def current_exchange_rate_and_history(
        currency_id: int,
        start_date: Optional[date] = Query(None,
                                           description="Дата начала фильтрации"),
        end_date: Optional[date] = Query(None,
                                         description="Дата окончания фильтрации"),
        session: As = Depends(get_async_session)

):
    """ Получает текущий курс валюты и историю изменения курса через с фильтрацией по дате  """
    try:
        currency = await session.get(Currency, currency_id)
        if not currency:
            raise HTTPException(status_code=404, detail="Item not found")
        query = select(History_Currency).filter(
            History_Currency.name == currency.name)

        # Добавляем фильтрацию по диапазону дат
        if start_date and end_date:
            query = query.filter(
                History_Currency.date_of_creation.between(start_date,
                                                          end_date))
        elif start_date:
            query = query.filter(
                History_Currency.date_of_creation >= start_date)
        elif end_date:
            query = query.filter(History_Currency.date_of_creation <= end_date)

        result = await session.execute(query)
        history_currency = result.scalars().all()

        return {
            "currency": currency,
            "history_currency": history_currency
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail={"error": "Ошибка базы данных"})
