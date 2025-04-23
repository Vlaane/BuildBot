import asyncio
import uuid
import aiohttp
import logging
from aiogram.types import InputMediaPhoto, BufferedInputFile
from sqlalchemy import select, and_, or_

import config
import main
import requests
from time import time
from aiohttp import web
from db import AsyncSessionLocal
from message_processing import contains_phone_number
from models.application import Application
from models.gigachat_config import GigachatConfig
from models.item import Item
from models.user import User, Message
from gigachat_funcs import generate_application_description, call_gigachat_api
from datetime import datetime
from applications import show_application
import os

ROOT_USER_ID = os.getenv("ROOT_USER_ID")




application_chat_ids = []
COUNT_OTHER_MESSAGES = 7
token_info = None
akk = 'NmU4NTlkMmEtZWFhNi00M2RiLWJjZTUtNjJlOTdiMzBlOGQzOmNjYTk0MGVjLTY2ZGUtNDJjYy05M2RiLTYwMjFmZDc3Y2FkMw=='


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Получение токена авито
def get_token_info():
    global token_info
    if token_info is None or token_info['expires_in'] >= time():
        token_url = "https://api.avito.ru/token"

        params = {
            "client_id": config.AVITO_CLIENT_ID,
            "client_secret": config.AVITO_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        logger.info(f"Client ID: {config.AVITO_CLIENT_ID}, Client Secret: {config.AVITO_CLIENT_SECRET}")
        response = requests.post(token_url, data=params)
        if response.status_code == 200:
            token_info = response.json()
            token_info['expires_in'] += time()
            logger.info(f"Token info: {token_info}")
        else:
            logger.error(f"Ошибка: {response.status_code}, {response.text}")

    return token_info


def get_gigachat_key():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': 'Basic NmU4NTlkMmEtZWFhNi00M2RiLWJjZTUtNjJlOTdiMzBlOGQzOmNjYTk0MGVjLTY2ZGUtNDJjYy05M2RiLTYwMjFmZDc3Y2FkMw=='
    }

    try:
        # Отключаем проверку сертификатов
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        logger.info("Токен GigaChat успешно получен")
        return response.json().get('access_token')
    except requests.exceptions.SSLError as ssl_error:
        logger.error(f"Ошибка SSL при получении ключа Gigachat: {ssl_error}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении ключа Gigachat: {e}")
        return None

# Получание списка чатов авито
def get_chats(user_id):
    global token_info
    get_token_info()
    get_chats_url = f'https://api.avito.ru/messenger/v2/accounts/{user_id}/chats'

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }

    params = {
        "chat_type": 'u2i'
    }

    response = requests.get(get_chats_url, headers=headers, params=params)

    if response.status_code != 200:
        logger.info(f"Failed to retrieve data: {response.status_code}")
        return

    chats_data = response.json()

    return chats_data


# Получение сообщений из чата авито
def get_messages(user_id, chat_id):
    global token_info
    get_token_info()
    get_messages_url = f'https://api.avito.ru/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages'

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }

    response = requests.get(get_messages_url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to retrieve data: {response.status_code}")
        if response.status_code == 403:
            token_url = "https://api.avito.ru/token"

            params = {
                "client_id": config.AVITO_CLIENT_ID,
                "client_secret": config.AVITO_CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
            response = requests.post(token_url, data=params)

            if response.status_code == 200:
                token_info = response.json()
                token_info['expires_in'] += time()

                get_messages_url = f'https://api.avito.ru/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages'

                headers = {
                    "Authorization": f"Bearer {token_info['access_token']}"
                }

                response = requests.get(get_messages_url, headers=headers)
                messages_data = response.json()
                # logger.info(f'MESSAGES_DATA: {messages_data}')
                return messages_data
            else:
                return

    messages_data = response.json()
    # logger.info(f'MESSAGES_DATA: {messages_data}')
    return messages_data


# Получение информации о чате авито
def get_chat(user_id, chat_id):
    global token_info
    get_token_info()
    get_chat_url = f'https://api.avito.ru/messenger/v2/accounts/{user_id}/chats/{chat_id}'

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }

    response = requests.get(get_chat_url, headers=headers)

    if response.status_code != 200:
        logger.info(f"Failed to retrieve data: {response.status_code}")
        return

    chat_data = response.json()

    return chat_data


# Отправка сообщения в чате авито

async def send_message(user_id: int, chat_id: str, text: str):
    """
    Отправляет текстовое сообщение в чат Авито.

    :param user_id: ID пользователя Авито
    :param chat_id: ID чата Авито
    :param text: текст сообщения для отправки
    """
    get_token_info()
    send_message_url = f'https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages'

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}",
        'Content-Type': 'application/json',
    }

    body = {
        "message": {
            "text": text
        },
        "type": "text"
    }

    # Используем aiohttp для асинхронного запроса
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(send_message_url, headers=headers, json=body) as response:
            if response.status == 200:
                logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
                return await response.json()
            else:
                text_resp = await response.text()
                logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {response.status} {text_resp}")
                return None


# async def send_message(user_id, chat_id, text):
#     return
#
#     get_token_info()
#     send_message_url = f'https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages'
#
#     headers = {
#         "Authorization": f"Bearer {token_info['access_token']}",
#         'Content-Type': 'application/json',
#     }
#
#     body = {
#         "message": {
#             "text": text
#         },
#         "type": "text"
#     }
#
#     response = requests.post(send_message_url, headers=headers, json=body)
#
#     if response.status_code != 200:
#         logger.info(f"Failed to retrieve data: {response.status_code}")
#         return
#
#     send_data = await response.json()
#
#     return send_data


# Получаение имени пользователя собеседника из chat_info
def get_username(chat_info, user_id):
    users = chat_info['users']
    for u in users:
        if u['id'] != user_id:
            return u['name']

    return None


def count_author_messages(messages, author_id):
    counter = 0
    for m in messages:
        if m['author_id'] == author_id:
            counter += 1
    return counter


def phone_contains_in_messages(messages, author_id):
    for m in messages:
        if m['author_id'] == author_id:
            if m['type'] == "text" and contains_phone_number(m['content'].get('text')):
                return True
    return False


def get_application_content(messages, author_id, message_number: int = 1):
    author_message_counter = 0
    logger.info(f"Содержимое message: {messages}")
    for m in messages:
        if m['author_id'] == author_id and m['type'] != "deleted":
            application_content = m['content'].get('text')
            author_message_counter += 1
            logging.info(
                f'{author_message_counter} {message_number} {application_content} - переходим к проверке условий.')
            if m['type'] == "text" and author_message_counter == message_number and application_content:
                logging.info(f'{author_message_counter} {message_number} {application_content}')
                return application_content
    return False


def find_handled_message(message_id, chat_id):
    for obj in application_chat_ids:
        if obj['message_id'] == message_id and obj['chat_id'] == chat_id:
            return True
    return False


# Удаляет записи сообщений из application_chat_ids, если счетчик <= 0
# def drop_old_handled_messages(message_id, chat_id):
#     for i in range(len(application_chat_ids)):
#         try:
#             if application_chat_ids[i]['message_id'] != message_id or application_chat_ids[i]['chat_id'] != chat_id:
#                 application_chat_ids[i]['counter'] -= 1
#                 if application_chat_ids[i]['counter'] <= 0:
#                     application_chat_ids.pop(i)
#         except Exception as e:
#             logger.info(f"drop_old_handled_messages error:{e}")
def drop_old_handled_messages(message_id, chat_id):
    for i in range(len(application_chat_ids) - 1, -1, -1):  # идём с конца к началу
        try:
            obj = application_chat_ids[i]
            if obj['message_id'] != message_id or obj['chat_id'] != chat_id:
                obj['counter'] -= 1
                if obj['counter'] <= 0:
                    application_chat_ids.pop(i)
        except Exception as e:
            logger.info(f"drop_old_handled_messages error: {e}")

async def process_client_message(avito_user_id: int, avito_chat_id: str, incoming_text: str, prompt1: str, gigachat_key: str):
    logger.info(f"process_client_message вызвана для пользователя {avito_user_id} в чате {avito_chat_id}")
    """
    Обрабатывает входящее сообщение от клиента Авито через GigaChat.

    :param avito_user_id: ID клиента Авито
    :param avito_chat_id: ID чата Авито
    :param incoming_text: текст входящего сообщения
    :param prompt: системный промпт для GigaChat
    :param gigachat_key: ключ API GigaChat
    :return: ответ от GigaChat (строка)
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 1. Найти или создать пользователя
            result = await session.execute(
                select(User).filter(User.avito_user_id == avito_user_id)
            )
            user = result.scalars().first()

            if not user:
                user = User(
                    avito_user_id=avito_user_id,
                    avito_chat_id=avito_chat_id,
                    phone=None,
                    name=None,
                    city=None,
                    created=int(datetime.now().timestamp())
                )
                session.add(user)
                await session.flush()  # чтобы получить user.id

            # 2. Получить историю сообщений из базы (отсортирована по времени)
            result = await session.execute(
                select(Message).filter(Message.user_id == user.id).order_by(Message.created)
            )
            messages = result.scalars().all()

            # 3. Добавить новое входящее сообщение в историю
            new_message = Message(
                user_id=user.id,
                content=incoming_text,
                created=int(datetime.now().timestamp()),
                direction='in'
            )
            session.add(new_message)
            await session.flush()

            # 4. Подготовить историю для GigaChat в формате [{"role":..., "content":...}, ...]
            history_for_gigachat = []
            for msg in messages:
                role = "user" if msg.direction == "in" else "assistant"
                history_for_gigachat.append({"role": role, "content": msg.content})
            # Добавляем новое входящее сообщение
            history_for_gigachat.append({"role": "user", "content": incoming_text})

            # 5. Вызываем GigaChat API с историей и промптом
            response_text = await call_gigachat_api(history_for_gigachat, prompt1, gigachat_key)
            logger.info(f"Ответ от GigaChat: {response_text}")

            # 6. Сохраняем ответ GigaChat в базе
            response_message = Message(
                user_id=user.id,
                content=response_text,
                created=int(datetime.now().timestamp()),
                direction='out'
            )
            session.add(response_message)

        await session.commit()

    logger.info(f"GigaChat ответ клиенту {avito_user_id}: {response_text}")
    return response_text

async def get_prompt1_from_db():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(GigachatConfig).filter(GigachatConfig.id == 1)
            )
            gigachat_config = result.scalars().first()
            if gigachat_config:
                return gigachat_config.prompt1
    return None



# Обработка вебхука сообщений с авито
async def handle_webhook_message(request):
    global token_info
    get_token_info()
    data = await request.json()

    # Получаем данные сообщения
    value = data.get('payload')['value']

    if value['type'] == 'system' or value['type'] == 'deleted':
        logger.info("Системное или удалённое сообщение, пропускаем")
        return web.json_response({"ok": True})

    m_id = value['id']
    chat_id = value['chat_id']
    user_id = value['user_id']
    author_id = value['author_id']
    created = int(time() * 1000)
    m_type = value['type']
    # Определяем тип контента сообщения
    if m_type == 'text':
        content = value['content']['text']
    elif m_type == 'image':
        content = value['content']['image']['sizes']['1280x960']
    else:
        content = "Unsupported type of file"

    # logger.info(f'Content: {content}')
    # logger.info(f'Chat id: {chat_id}')

    # Не обрабатываем свои же сообщения
    if author_id == user_id:
        logger.info("Сообщение от бота, пропускаем")
        return web.json_response({"ok": True})


    # Если нет id чата, то не обрабатывем данные
    if chat_id is None or chat_id == '0':
        logger.info('chat_id отсутствует')
        return

    # Если сообщения не обрабатывали, то добавляем его в массив обработанных
    if not find_handled_message(m_id, chat_id):
        logger.info('Сообщение еще не обрабатывали')
        application_chat_ids.append({
            'message_id': m_id,
            'chat_id': chat_id,
            'counter': COUNT_OTHER_MESSAGES,
        })
        drop_old_handled_messages(m_id, chat_id)
    else:  # Если обрабатывали, то меняем счетчик
        logger.info('Сообщение уже обрабатывали')
        for i in range(len(application_chat_ids)):
            try:
                if application_chat_ids[i]['message_id'] != m_id and application_chat_ids[i]['chat_id'] != chat_id:
                    application_chat_ids[i]['counter'] = COUNT_OTHER_MESSAGES
            except Exception as e:
                logger.info("Reset counter for old webhook:", e)
        return web.json_response({"ok": True})

    logger.info('Переходим к проверке есть ли уже эта заявка')
    d = {'is_new': True}
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем заявки по id чата авито
            result = await session.execute(
                select(Application).filter(Application.avito_chat_id == chat_id)
            )
            application_db = result.scalars().first()
            logger.info(f'Заявка в бд: {application_db}')
            # Если заявка сущетвут в бд, то ставим флаг is_new = Flase
            if application_db is not None:
                d['is_new'] = False

    # messages = get_messages(user_id, chat_id)['messages'][::-1]
    # Если заявка новая

    if d['is_new']:
        logger.info('Заявка новая')
        # Получаем список сообщений и считаем кол-во сообщений от собеседника
        try:
            messages = get_messages(user_id, chat_id)
            if messages:
                messages = messages['messages'][::-1]
            else:
                logger.info(messages)
                messages = get_messages(user_id, chat_id)
                if messages:
                    messages = messages[::-1]
        except Exception as e:
            try:
                messages = get_messages(user_id, chat_id)[::-1]
            except Exception as e:
                logger.info(messages)
                logger.error(f'ПРОИЗОШЛА ОШИБКА на 271 строке {e}')
                return

                # logger.info(f'MESSAGES {messages}')

        phone_contains = phone_contains_in_messages(messages, author_id)
        logger.info(f'PHONE_CONTAINS {phone_contains}')

        async with AsyncSessionLocal() as session:
            async with session.begin():
                result = await session.execute(
                    select(GigachatConfig).filter(GigachatConfig.id == 1)
                )
                gigachat_config = result.scalars().first()
                if gigachat_config:
                    prompt = gigachat_config.prompt
                    prompt1 = gigachat_config.prompt1
                    # prompt = GigachatConfig.prompt

        new_application_content = get_application_content(messages, author_id, message_number=1)
        logger.info(f"Полученное содержимое заявки: {new_application_content}")
        # logger.info(f'{new_application_content}')

        # Чат считается новым если кол-во сообщений было менее или равно 1 и не от нас
        logger.info(f"phone_contains: {phone_contains}")
        logger.info(f"author_id: {author_id}, user_id: {user_id}")
        logger.info(f"new_application_content: {new_application_content}")
        if phone_contains and author_id != user_id and new_application_content:
            logger.info('Все проверки на 266 строке пройдены')

            # Создаем описание
            chat = get_chat(user_id, chat_id)
            username = get_username(chat, user_id)

            formatted_prompt = prompt.format(client_name=username, current_datetime=datetime.now().date())
            key = "NmU4NTlkMmEtZWFhNi00M2RiLWJjZTUtNjJlOTdiMzBlOGQzOmNjYTk0MGVjLTY2ZGUtNDJjYy05M2RiLTYwMjFmZDc3Y2FkMw=="
            logger.info("Запуск генерации описания через GigaChat")
            application_description = await generate_application_description(messages, formatted_prompt, key)
            logger.info(f"Результат генерации: {application_description}")

            # Создаем новую заявку
            await add_new_application(
                user_id=user_id,
                chat_id=chat_id,
                m_id=m_id,
                m_type=m_type,
                content=new_application_content,
                description=application_description,
                author_id=author_id,
                created=created,
                chat=chat,
                username=username
            )

            # Отвечаем клиенту через консультанта GigaChat
            response_text = await process_client_message(
                avito_user_id=user_id,
                avito_chat_id=chat_id,
                incoming_text=content,
                prompt1=prompt1,
                gigachat_key=akk
            )
            await send_message(user_id, chat_id, response_text)


            return web.json_response({"ok": True})
        else:
            logger.info('Условия для создания заявки не выполнены, заявка не создаётся')
        response_text = await process_client_message(
            avito_user_id=user_id,
            avito_chat_id=chat_id,
            incoming_text=content,
            prompt1=prompt1,
            gigachat_key=akk
        )
        await send_message(user_id, chat_id, response_text)

        return web.json_response({"ok": True})
    else:
        prompt1 = await get_prompt1_from_db()
        if not prompt1:
            logger.error("Промпт1 не найден в базе")
            return web.json_response({"ok": True})

        response_text = await process_client_message(
            avito_user_id=user_id,
            avito_chat_id=chat_id,
            incoming_text=content,
            prompt1=prompt1,
            gigachat_key=akk
        )
        await send_message(user_id, chat_id, response_text)

    logger.info(data.get('payload'))

    return web.json_response({"ok": True})


# Оповещение админа заявкой
async def notify_admins(session, application, bot):
    if ROOT_USER_ID:
        try:
            await show_application(
                session=session,
                application=application,
                bot=bot,
                chat_id=int(ROOT_USER_ID),
                is_root_admin=True,
            )
            logger.info(f"Отправлено уведомление ROOT_USER_ID {ROOT_USER_ID}")
        except Exception as e:
            logger.error(f"Ошибка отправки ROOT_USER_ID: {e}", exc_info=True)
    else:
        logger.error("ROOT_USER_ID не задан в переменных окружения")


# Добавление новой заявки
async def add_new_application(user_id, chat_id, m_id, m_type, content, author_id, created, description, chat, username):
    # chat = get_chat(user_id, chat_id)
    # username = get_username(chat, user_id)
    logger.info(f"Данные для сохранения: chat_id={chat_id}, description={description}")
    if not description:
        logger.error("Пустое описание от GigaChat!")

    logger.info(f"Сохранение в БД: {content}")

    from applications import show_application

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Application).filter(or_(
                    Application.avito_chat_id == chat_id,
                    Application.avito_message_id == m_id,
                ))
            )
            application_db = result.scalars().first()

            if application_db is None and int(chat['context']['value']['id']) != 0:

                result = await session.execute(
                    select(Item).filter(Item.avito_item_id == int(chat['context']['value']['id']))
                )
                item = result.scalars().first()

                item_location = "None"
                if item is not None:
                    item_location = item.location
                else:
                    item = Item(
                        avito_item_id=int(chat['context']['value']['id']),
                        url=chat['context']['value']['url'],
                        location="None"
                    )
                    session.add(item)

                application = Application(
                    avito_chat_id=chat_id,
                    avito_message_id=m_id,
                    in_working=False,
                    working_user_id=-1,
                    item_name=chat['context']['value']['title'],
                    item_location=item_location,
                    item_id=int(chat['context']['value']['id']),
                    type=m_type,
                    content=description,
                    author_id=str(author_id),
                    user_id=str(user_id),
                    created=int(created),
                    last_message_time=int(created),
                    last_message_text=content,
                    username=username,
                )

                session.add(application)
                await session.flush()

                if item_location == "None":
                    await notify_admins(session, application, main.bot)
                else:
                    await notify_admins(session, application, main.bot)

                # if item_location == "None":
                #     # Отправляем уведомление админу о новой заявке с неизвестной локацией
                #     result = await session.execute(
                #         select(User).filter(
                #             User.admin == True,
                #             User.banned == False
                #         )
                #     )
                #     admins = result.scalars().all()
                #     for admin in admins:
                #         await show_application(
                #             session=session,
                #             application=application,
                #             bot=main.bot,
                #             chat_id=admin.telegram_chat_id,
                #             is_root_admin=True,
                #         )
                # else:
                #     # Отправляем уведомление админу о новой заявке с известной локацией
                #     result = await session.execute(
                #         select(User).filter(
                #             User.admin == True,
                #             User.banned == False
                #         )
                #     )
                #     admins = result.scalars().all()
                #     for admin in admins:
                #         await show_application(
                #             session=session,
                #             application=application,
                #             bot=main.bot,
                #             chat_id=admin.telegram_chat_id,
                #             is_root_admin=True,
                #         )

        await session.commit()
        logger.info("Заявка успешно добавлена")


# Регистрация вебхука в авито
async def register_webhook():
    global token_info
    url = "https://api.avito.ru/messenger/v3/webhook"
    get_token_info()
    access_token = token_info['access_token']
    webhook_url = f"{config.WEBHOOK_HOST}{config.WEBHOOK_PATH}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "url": webhook_url
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                logger.info("Webhook registered successfully")
            else:
                response_text = await response.text()
                logger.info("Failed to register webhook", response_text)


async def index_function(request):
    return web.json_response({"ok": True})


# Запуск сервера
async def start_avito_webhook(webhook_function, robokassa_function=None):
    await register_webhook()
    app = web.Application()
    app.router.add_post(config.WEBHOOK_PATH, webhook_function)
    # app.router.add_post(config.ROBOKASSA_PATH, robokassa_function)
    app.router.add_get('/', index_function)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=3001)
    await site.start()
    logger.info("Server running on port 3001")
    while True:
        await asyncio.sleep(1500)


if __name__ == '__main__':
    asyncio.run(start_avito_webhook(handle_webhook_message))
