from aiogram.fsm.state import State, StatesGroup


# Все состояние
class States(StatesGroup):
    # Состояние ввода сообщения в чате авито
    message = State()
    avito_info = State()
    admin_change = State()
    previous_state = State()
    sending_text = State()
    change_prompt = State()  # Добавлено состояние для изменения промпта

    # Здесь храняться id сообщений
    ids = State()
    admin_ids = State()
    sending_ids = State()
    prompt_ids = State()  # Добавлено состояние для id промпта
