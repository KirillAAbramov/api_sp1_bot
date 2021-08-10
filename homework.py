import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_statuses = {
        'reviewing': 'Работа взята в ревью',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось, работа зачтена!'
    }
    if homework['status'] in homework_statuses:
        if homework['status'] == 'rejected' or 'approved':
            return (f'У вас проверили работу "{homework_name}"!\n\n'
                    f'{homework_statuses[homework["status"]]}')
        else:
            return f'{homework_statuses["reviewing"]}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logging.info('Новое сообщение!')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Поехали!')
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get('homeworks'):
                try:
                    send_message(
                        parse_homework_status(
                            new_homework.get('homeworks')[0]
                        )
                    )
                except IndexError:
                    logging.error('Такую домашку ты не делал!')
                    send_message('Такую домашку ты не делал')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )  # обновить timestamp
            time.sleep(10)

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


if __name__ == '__main__':
    main()
