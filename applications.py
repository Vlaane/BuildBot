import os
import time
import uuid
from asyncio import sleep
from aiogram import Bot
from aiogram.enums import ParseMode
# import requests
# import avito
# import kb
# from message_processing import send_state_message, send_state_media
# from models.addiction import Addiction
# from models.application import Application
# from db import AsyncSessionLocal
# from models.item_addiction import ItemAddiction
# from models.mask import Mask
# from models.subscription import Subscription
# from models.user import User
# from models.work import Work
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # или DEBUG для более подробных логов
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',





async def show_application(session, application, bot, chat_id, is_root_admin):
    try:
        text = (
            "<b>Локация: "
            + " ".join(application.item_location.split(", "))
            + "\n\n"
            + f"Заявка от пользователя {application.username}:</b>\n\n{application.content}"
        )
        logger.info(f"Отправка сообщения админу {chat_id}")
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )
        await sleep(0.3)
    except Exception as e:
        logger.error(f"Ошибка в show_application: {e}", exc_info=True)






# Функция для отображения заявки пользователю
# session - сессия базы данных для сохранения данных
# application - объект заявки, содержащий информацию о типе, содержимом и местоположении
# user_city - город пользователя, используемый для фильтрации заявок по локации
# bot - экземпляр бота для отправки сообщений
# chat_id - ID чата, куда будет отправлено сообщение
# is_root_admin - флаг, указывающий, является ли пользователь главным администратором
# async def show_application(session, application, user_city, bot: Bot, chat_id, is_root_admin=False):
#     try:
#         # Получение списка локаций из заявки
#         location = application.item_location.split(', ')
#
#         # Если пользователь не является администратором и его город не совпадает с локацией заявки,
#         # ничего не отправляется
#         if user_city not in location and not is_root_admin:
#             return
#
#         # Формирование текста для отправки
#         text = "<b>"
#
#         # Если пользователь главный администратор, добавляем информацию о локации в сообщение
#         if is_root_admin:
#             text += "Локация: "
#             for loc in location:
#                 text += f"{loc} "
#             text += "\n\n"
#
#         # Создание клавиатуры для взаимодействия с заявкой
#         keyboard = kb.create_application_keyboard()
#
#         # Обработка заявки в зависимости от её типа
#         if application.type == 'text':
#             # Форматирование текста заявки
#             text += f"Заявка от пользователя {application.username}:</b>\n\n{application.content}"
#
#             # Отправка сообщения с текстовой заявкой
#             m = await bot.send_message(
#                 chat_id=chat_id,
#                 text=text,
#                 reply_markup=keyboard,
#                 parse_mode=ParseMode.HTML,
#             )
#
#             # Сохранение информации о сообщении в базе данных
#             addiction = Addiction(
#                 application_id=application.id,
#                 telegram_message_id=m.message_id,
#                 telegram_chat_id=m.chat.id
#             )
#             session.add(addiction)
#
#         elif application.type == 'image':
#             # Загрузка изображения по URL
#             response = requests.get(application.content)
#             if response.status_code != 200:
#                 print(f"Не удалось скачать картинку. Код ошибки: {response.status_code}")
#                 return
#
#             # Чтение содержимого файла
#             file_bytes = response.content
#             name = str(uuid.uuid4())
#
#             # Форматирование текста для изображения
#             text += f"Заявка от пользователя {application.username}:</b>"
#
#             # Создание объекта изображения для отправки
#             media = InputMediaPhoto(
#                 media=BufferedInputFile(file_bytes, filename=f'image_{name}.jpg'),
#             )
#
#             # Отправка изображения и получение идентификатора сообщения
#             m = (await bot.send_media_group(
#                 chat_id=chat_id,
#                 media=[media]
#             ))[0]
#
#             # Сохранение информации о сообщении с изображением
#             addiction1 = Addiction(
#                 application_id=application.id,
#                 telegram_message_id=m.message_id,
#                 telegram_chat_id=m.chat.id,
#             )
#
#             # Отправка текста заявки после изображения
#             m = await bot.send_message(
#                 chat_id=chat_id,
#                 text=text,
#                 reply_markup=keyboard,
#                 parse_mode=ParseMode.HTML,
#             )
#
#             # Сохранение информации о текстовом сообщении
#             addiction2 = Addiction(
#                 application_id=application.id,
#                 telegram_message_id=m.message_id,
#                 telegram_chat_id=m.chat.id,
#             )
#             session.add(addiction1)
#             session.add(addiction2)
#
#         else:
#             # Если тип заявки не поддерживается, отправляется уведомление с текстом
#             text += (f"Заявка от пользователя {application.username}:</b>\n\nДанный тип сообщения невозможно "
#                      f"обработать в Telegram, но вы можете взять заявку")
#
#             # Отправка уведомления
#             m = await bot.send_message(
#                 chat_id=chat_id,
#                 text=text,
#                 reply_markup=keyboard,
#                 parse_mode=ParseMode.HTML,
#             )
#
#             # Сохранение информации о сообщении
#             addiction = Addiction(
#                 application_id=application.id,
#                 telegram_message_id=m.message_id,
#                 telegram_chat_id=m.chat.id,
#             )
#             session.add(addiction)
#
#         # Небольшая задержка перед следующей отправкой для предотвращения перегрузки
#         await sleep(0.3)
#     except Exception as e:
#         print(e)



# Функция для показа сообщений из чата Avito и действий по заявке
# state - текущее состояние FSM
# bot - экземпляр Telegram-бота
# avito_chat_id - идентификатор чата на Avito
# avito_user_id - идентификатор пользователя на Avito
# telegram_chat_id - идентификатор чата в Telegram
# author_id - идентификатор автора сообщения на Avito
# username - имя пользователя автора сообщения
# async def show_messages_for_application(state, bot: Bot, avito_chat_id, avito_user_id, telegram_chat_id, author_id, username):
#     # Получение списка сообщений из чата Avito
#     messages = avito.get_messages(
#         chat_id=avito_chat_id,
#         user_id=avito_user_id,
#     )['messages']
#
#     # Реверс списка сообщений, чтобы начинать с самого раннего
#     messages.reverse()
#
#     # Определение текущей директории и путей к файлам шаблонов документов
#     current_dir = os.getcwd()
#     path_1 = os.path.join(current_dir, "files/dogovor.docx")
#     path_2 = os.path.join(current_dir, "files/act.docx")
#     path_3 = os.path.join(current_dir, "files/raspiska.docx")
#
#     # Чтение файлов шаблонов документов в байтовом формате
#     file1_bytes = open(path_1, "rb").read()
#     file2_bytes = open(path_2, "rb").read()
#     file3_bytes = open(path_3, "rb").read()
#
#     # Создание медиа-документов для отправки в Telegram
#     doc1 = InputMediaDocument(media=BufferedInputFile(file1_bytes, filename="Образец договора возмездного оказания услуг.docx"))
#     doc2 = InputMediaDocument(media=BufferedInputFile(file2_bytes, filename="Акт приёмки-сдачи услуг.docx"))
#     doc3 = InputMediaDocument(media=BufferedInputFile(file3_bytes, filename="Расписка о получении денежных средств.docx"))
#
#     # Группировка документов в список для отправки
#     media = [doc1, doc2, doc3]
#
#     # Отправка документов пользователю
#     await send_state_media(
#         state=state,
#         chat_id=telegram_chat_id,
#         media=media,
#         bot=bot
#     )
#
#     # Текст с инструкциями для действий по заявке
#     text = (
#         "*Действия с заявкой:*\n_Завершить работу_ \- работа по заявке полностью выполнена, оплата получена\n"
#         "_Отказаться от заявки_ \- отказ от работы с заявкой, вы больше не сможете взять эту заявку, "
#         "вам будет возвращена половина заплаченной комиссии"
#     )
#
#     # Отправка текста с клавиатурой для выбора действий
#     keyboard = kb.create_application_actions_keyboard()
#     await send_state_message(
#         state=state,
#         keyboard=keyboard,
#         chat_id=telegram_chat_id,
#         bot=bot,
#         text=text,
#         parse_mode=ParseMode.MARKDOWN_V2,
#     )
#
#     # Обработка каждого сообщения из чата Avito
#     for message in messages:
#         await sleep(0.3)  # Искусственная задержка для предотвращения ограничения на частоту запросов
#         # Определение имени автора сообщения
#         name = username if message['author_id'] == int(author_id) else "Вас"
#
#         # Обработка текстового сообщения
#         if message['type'] == 'text':
#             text = f"<b>Сообщение от {name}:</b>\n\n{message['content']['text']}"
#             await send_state_message(
#                 chat_id=telegram_chat_id,
#                 bot=bot,
#                 state=state,
#                 text=text,
#                 parse_mode=ParseMode.HTML,
#             )
#
#         # Обработка сообщения с изображением
#         elif message['type'] == 'image':
#             data = message['content']['image']['sizes']['1280x960']
#             text = f"<b>Сообщение от {name}:</b>"
#             response = requests.get(data)
#             if response.status_code != 200:
#                 print(f"Не удалось скачать картинку. Код ошибки: {response.status_code}")
#                 return
#             file_bytes = response.content
#             name = str(uuid.uuid4())
#             media = InputMediaPhoto(
#                 media=BufferedInputFile(file_bytes, filename=f'image_{name}.jpg'),
#             )
#             await send_state_message(
#                 chat_id=telegram_chat_id,
#                 bot=bot,
#                 state=state,
#                 text=text,
#                 parse_mode=ParseMode.HTML,
#             )
#             await send_state_media(
#                 chat_id=telegram_chat_id,
#                 bot=bot,
#                 state=state,
#                 media=[media]
#             )
#
#         # Обработка неподдерживаемых типов сообщений
#         else:
#             text = f"<b>Сообщение от {name}:</b>\n\nТип сообщения не поддерживается"
#             await send_state_message(
#                 state=state,
#                 chat_id=telegram_chat_id,
#                 bot=bot,
#                 text=text,
#                 parse_mode=ParseMode.HTML,
#             )
#
#
# # Отправка сообщения в чат авито
# async def send_message_for_application(avito_user_id, avito_chat_id, text):
#     await avito.send_message(
#         user_id=avito_user_id,
#         chat_id=avito_chat_id,
#         text=text,
#     )
#
#
#
#
#
