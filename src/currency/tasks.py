import asyncio
import requests
import xml.etree.ElementTree as ET

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import delete, text

from src.database import Session
from src.models.models import Currency

celery_app = Celery('tasks', broker='redis://localhost:6379/0')


async def run_main():
    """
    Обновление базы данных в таблице currency данными по курсам валют раз в 30 минут.
    """
    async with Session() as session:
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
        'schedule': crontab(minute='*/30'),
    },
}
# Установка часового пояса на московский
celery_app.conf.timezone = 'Europe/Moscow'  # Московский часовой пояс
