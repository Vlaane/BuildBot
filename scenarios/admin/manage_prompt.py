from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from db import AsyncSessionLocal
from message_processing import send_state_message, add_state_id, reset_state
from models.gigachat_config import GigachatConfig
from states import States

def load_handlers(dp, bot):
    router = Router()

    @router.message(Command('change_prompt'), StateFilter(None, States.message))
    async def change_prompt_command(message: types.Message, state: FSMContext):
        try:
            await add_state_id(
                state=state,
                message_id=message.message_id,
                state_name="prompt_ids"
            )

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(
                        select(GigachatConfig).filter(GigachatConfig.id == 1)
                    )
                    gigachat_config = result.scalars().first()

                    if not gigachat_config:
                        await send_state_message(
                            message=message,
                            text="Конфигурация не найдена.",
                            state=state,
                            state_name="prompt_ids"
                        )
                        return

                    current_prompt = gigachat_config.prompt

            await send_state_message(
                message=message,
                text=f"Текущий промпт: {current_prompt}\nВведите новый промпт или напишите 'отмена' для отмены:",
                state=state,
                state_name="prompt_ids"
            )
            await state.set_state(States.change_prompt)
        except Exception as e:
            print(e)

    @router.message(States.change_prompt)
    async def update_prompt(message: types.Message, state: FSMContext):
        try:
            new_prompt = message.text

            if new_prompt.lower() == 'отмена':
                await send_state_message(
                    state=state,
                    message=message,
                    text="Изменение промпта отменено",
                    state_name="prompt_ids"
                )
                await reset_state(state=state)
                return

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(
                        select(GigachatConfig).filter(GigachatConfig.id == 1)
                    )
                    gigachat_config = result.scalars().first()

                    if not gigachat_config:
                        return

                    gigachat_config.prompt = new_prompt

                await session.commit()

            await send_state_message(
                state=state,
                message=message,
                text="Промпт успешно изменен",
                state_name="prompt_ids"
            )

            await reset_state(state=state)
        except Exception as e:
            print(e)
            await send_state_message(
                state=state,
                message=message,
                text="Ошибка, повторите ввод",
                state_name="prompt_ids"
            )
            await state.set_state(States.change_prompt)

    dp.include_router(router)



