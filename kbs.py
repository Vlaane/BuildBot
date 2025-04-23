from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder
from aiogram import types

def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Просмотр кол-ва участников", callback_data="count_numbers"),
        InlineKeyboardButton(text="Промпт", callback_data="show_prompt_menu"),
    )
    builder.row(
        InlineKeyboardButton(text="API's", callback_data="api_keys"),
        InlineKeyboardButton(text="Статистика", callback_data="stats")
    )
    return builder.as_markup()


def prompt_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Посмотреть промпт", callback_data="view_prompt"),
        InlineKeyboardButton(text="Изменить промпт", callback_data="change_prompt"),
    )
    return builder.as_markup()


def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="show_prompt_menu"),
    )
    return builder.as_markup()


def user_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Профиль", callback_data="profile"),
        InlineKeyboardButton(text="Оферта", callback_data="show_oferta"),
    )
    builder.row(
        InlineKeyboardButton(text="Реферальная ссылка", callback_data="referal"),
        InlineKeyboardButton(text="Баланс и оплаты", callback_data="payments"),
    )
    builder.row(
        InlineKeyboardButton(text="Перезагрузка бота", callback_data="reload_bot"),
        InlineKeyboardButton(text="Пожелания от пользователей", callback_data="Wish_list"),
    )
    return builder.as_markup()


def get_registration_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text="Зарегистрироваться",
        request_contact=True
    ))
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
