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

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

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
    except Exception as error:
        error_msg = f'Возникла ошибка при отправке сообщения: {error}'
        logger.error(error_msg)
        raise KeyError(error_msg)


def get_api_answer(current_timestamp):
    """Отправка запроса к эндпоинту API Яндекс Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            error_msg = 'Неверный статус ответа от API'
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    except Exception as error:
        error_msg = f'Возникла ошибка при запросе к основному API: {error}'
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    response = response.json()
    return response


def check_response(response):
    """Проверка содержимого ответа API."""
    if not isinstance(response, dict):
        error_msg = 'Неверный ответ API'
        logger.error(error_msg)
        raise TypeError(error_msg)
    if 'homeworks' not in response:
        error_msg = 'У homeworks отсутствует ключ'
        logger.error(error_msg)
        raise KeyError(error_msg)
    if not isinstance(response['homeworks'], list):
        error_msg = 'Неверный ответ API на уровне homeworks'
        logger.error(error_msg)
        raise TypeError(error_msg)
    homework = response.get('homeworks')
    return homework


def parse_status(homework):
    """Проверка статуса домашней работы на сервере."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        error_msg = 'Неверный ответ сервера'
        logger.error(error_msg)
        raise KeyError(error_msg)
    if homework_status not in HOMEWORK_STATUSES.keys():
        error_msg = 'Недопустимый статус работы'
        logger.error(error_msg)
        raise KeyError(error_msg)
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
        if token:
            return True
        else:
            return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_msg = 'Возникла ошибка при проверке токенов'
        logger.error(error_msg)
        raise KeyError(error_msg)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                send_message(BOT, parse_status(homework[0]))
            current_timestamp = response.get('current_date',
                                             current_timestamp)
            time.sleep(RETRY_TIME)

        except Exception as error:
            error_msg = f'Возникла ошибка в работе программы: {error}'
            logger.error(error_msg)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
