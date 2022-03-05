import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKENPR')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHATTOKEN')

UPDATE_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logging.basicConfig(
    level=logging.DEBUG,
    filename='bot_logs.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler('bot_logs.log')
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except telegram.error.TelegramError as error:
        logger.error(f'Возникла ошибка при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Отправка запроса к эндпоинту API Яндекс Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError('Неверный статус ответа от API')
    response = response.json()
    return response


def check_response(response):
    """Проверка содержимого ответа API."""
    if not isinstance(response, dict):
        raise TypeError('Неверный ответ API')
    if 'homeworks' not in response:
        raise KeyError('У homeworks отсутствует ключ')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Неверный ответ API на уровне homeworks')
    homework = response.get('homeworks')
    return homework


def parse_status(homework):
    """Проверка статуса домашней работы на сервере."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        raise KeyError('Неверный ответ сервера')
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError('Недопустимый статус работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    for token in tokens:
        if not token:
            return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    error_list = []
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                send_message(bot, parse_status(homework[0]))
            else:
                logger.info('Статус домашнего задания не обновился')
            error_list.clear()
            current_timestamp = response.get('current_date')
        except Exception as error:
            error_msg = f'Возникла ошибка в работе программы: {error}'
            logger.error(error_msg)
            if error_msg not in error_list:
                bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=error_msg
                )
                error_list.append(error_msg)
        finally:
            time.sleep(UPDATE_TIME)


if __name__ == '__main__':
    if check_tokens():
        main()
    else:
        logger.error('Ошибка при проверке токенов')
