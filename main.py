import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from sqlalchemy import select

from models.gigachat_config import GigachatConfig
from scenarios.admin import manage_prompt
from db import init_db, AsyncSessionLocal
import config
import avito

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def start_bot():
    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)

    manage_prompt.load_handlers(dp, bot)

    users = []

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(GigachatConfig)
            )

            gigachat_config = result.scalars().first()

            if not gigachat_config:
                new_gigachat_config = GigachatConfig(
                    prompt='''Я буду тебе отправлять историю переписки с клиентом, а ты должен в ответ отправить информацию в таком формате(который я прикреплю снизу), используя данные из диалога с клиентом. В ОТВЕТ ТЫ ДОЛЖЕН ОТПРАВИТЬ ТОЛЬКО ПОДВЕДЕННЫЙ ИТОГ В НУЖНОМ ФОРМАТЕ, БЕЗ КАКИХ-ЛИБО ДРУГИХ ВВОДНЫХ/ЗАКЛЮЧИТЕЛЬНЫХ СЛОВ. НЕЛЬЗЯ ОТПРАВЛЯТЬ КОНТАКТНЫЙ НОМЕР ТЕЛЕФОНА И СПОСОБ СВЯЗИ НИ В КОЕМ СЛУЧАЕ
Формат ответа:

<b>Локация:</b> Калининград; 
<b>Имя:</b> {client_name}(имя оставь как есть);
<b>Услуга:</b> (например, Поклейка флизелиновых обоев. снятие старых); 
<b>Объем работ:</b> 20м2;
<b>Сроки начала:</b> Если заказчик пишет завтра или другое время без конкретной даты или говорит что-то вроде "завтра"/"в ближайшие дни" и тд, то постарайся посчитать дату с учетом сегодняшней даты {current_datetime};
<b>Сроки окончания:</b> (если заказчик сообщит, если не сообщит, то пиши "Не указано". Если заказчик говорит что-то вроде "завтра"/"в ближайшие дни" и тд, то постарайся посчитать дату с учетом сегодняшней даты {current_datetime});
<b>Бюджет:</b> (если заказчик сообщит, если не сообщит, то пиши "Не указано");
<b>Дата и время поступления заявки:</b> (формат даты 02 марта 2025 года, без времени, только дата.) (сегодня {current_datetime});
''',
                prompt1 = "Ты консультант компании  которая занимается отделлочными работами, ты разговариваешь с клиентами"
                          "и консульируешь их, твоя цель получить от клиента по ходу разговора вид работ, бюджет. СААМОЕ ГЛАВНОЕ - "
                          "ТЫ ДОЛЖЕН ПОЛУЧИТЬ НОМЕР ТЕЛЕФОНА КЛИЕНТА"
                )
                session.add(new_gigachat_config)

        await session.commit()

    # Сообщаем каждому юзеру о том, что бот был перезагружен
    # for user in users:
    #     text = ("<b>Внимание!</b>\nБот был перезагружен, для корректной работы требуется очистить чат и запустить "
    #             "команду <b>/reload</b>")
    #     try:
    #         await sleep(0.6)
    #         await bot.send_message(
    #             chat_id=user['telegram_chat_id'],
    #             text=text,
    #             parse_mode=ParseMode.HTML
    #         )
    #     except Exception as e:
    #         print("Send restart message:", e)

    # Устанавливаем список команд
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="reload", description="Показать заявки"),
        BotCommand(command="cancel", description="Отмена текущего действия"),
    ])

    print("| - - - - - Starting - - - - - |")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main():
    await asyncio.gather(
        avito.start_avito_webhook(avito.handle_webhook_message),
        start_bot()
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
