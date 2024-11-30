import asyncio
from datetime import timedelta, datetime

from celery import Celery
from celery.schedules import crontab

from sqlalchemy import delete

from src.database import Session
from src.models.models import Currency
import xml.etree.ElementTree as ET
import requests

celery_app = Celery('tasks', broker='redis://localhost:6379/0')


async def run_main():
    """
    Обновление базы данных в таблице currency данными по курсам валют раз в 4 часа.
    """
    async with Session() as session:
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        response = requests.get(url)
        root = ET.fromstring(response.content)
        # удаляем все старые записи из таблицы
        await session.execute(delete(Currency))
        for valute in root.findall('.//Valute'):
            new_currency = Currency(name=valute.find('Name').text,
                                    rate=valute.find('Value').text)
            session.add(new_currency)
        await session.commit()


@celery_app.task
def main():
    # Запускаем асинхронную функцию
    #  Функция возвращает текущий цикл событий.
    #  Если цикл событий еще не создан, он будет создан автоматически
    loop = asyncio.get_event_loop()

    #  Эта команда запускает асинхронную функцию run_main и блокирует
    #  выполнение до тех пор, пока эта функция не завершится.
    loop.run_until_complete(run_main())


celery_app.conf.beat_schedule = {
    'main': {
        'task': 'src.currency.tasks.main',
        'schedule': crontab(minute='*/1'),
    },
}
