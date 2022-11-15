# Homework-Bot

## Описание:

Чат-бот Telegram для получения информации о проведенном код-ревью домашнего задания (Telegram API)

Проект размещен на [Heroku](https://www.heroku.com).

## Технологии и библиотеки:

- [Python](https://www.python.org/);
- [Requests](https://pypi.org/project/requests/),
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [python-telegram-bot](https://python-telegram-bot.org)
- [pySocks](https://pypi.org/project/PySocks/)

## Принцип работы:

Чат-бот Телеграм обращается к API, которое возвращает изменение статуса домашнего задания и сообщает проверено ли задание, провалено или принято.

## Как запустить программу:

1) Клонируйте репозитроий с программой:
```
git clone https://github.com/alkh0304/homework_bot
```
2) В созданной директории установите виртуальное окружение, активируйте его и установите необходимые зависимости:
```
python -m venv venv

source venv/Scripts/activate

pip install -r requirements.txt
```
3) Создайте чат-бота Телеграм
4) Создайте в директории файл .env и поместите туда необходимые токены в формате PRAKTIKUM_TOKEN = 'ххххххххх', TELEGRAM_TOKEN = 'ххххххххххх',
TELEGRAM_CHAT_ID = 'ххххххххххх'
5) Откройте файл homework.py и запустите код

### Пример ответа чат-бота:
{
   "homeworks":[
      {
         "id":123,
         "status":"approved",
         "homework_name":"username__hw_python_oop.zip",
         "reviewer_comment":"Всё нравится",
         "date_updated":"2020-02-13T14:40:57Z",
         "lesson_name":"Итоговый проект"
      }
   ],
   "current_date":1581604970
}

## Над проектом [Homework-Bot](https://github.com/alkh0304/homework_bot) работал:

[Александр Хоменко](https://github.com/alkh0304)