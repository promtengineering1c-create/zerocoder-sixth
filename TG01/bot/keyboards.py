from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

show_more_buttons = [{"text": "Опция 1", "callback_data": "option_1"}, {"text": "Опция 2", "callback_data": "option_2"}]
async def create_show_more_keyboard():
    keyboard = InlineKeyboardBuilder()
    for button_data in show_more_buttons:
        button = InlineKeyboardButton(text=button_data["text"], callback_data=button_data["callback_data"])
        keyboard.add(button)
    return keyboard.adjust().as_markup()

dynamic_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
])

bottom = ReplyKeyboardMarkup(keyboard=
    [
        [KeyboardButton(text="Привет")],
        [KeyboardButton(text="Пока")],
    ],
    resize_keyboard=True
    )

link_buttoms = InlineKeyboardMarkup(inline_keyboard=
    [
        [InlineKeyboardButton(text="Новости", url="https://t.me/")],
        [InlineKeyboardButton(text="Музыка", url="https://t.me/")],
        [InlineKeyboardButton(text="Видео", url="https://t.me/")],
    ]
   )