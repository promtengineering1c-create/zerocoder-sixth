from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from config.settings.base import FILES
from weather_api.client import get_weather_by_city
from weather_api.states import WeatherStates

from .services.db_students import get_student_or_none, save_student
from .services.files import save_user_photo
from .services.translator import translate_text
from .states import RegistrationFSM, TranslationFSM

router = Router()
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для запроса погоды.\n"
        "Нажми или напиши /weather, чтобы узнать текущую сводку."
        )

@router.message(Command("weather"))
async def cmd_weather_start(message: Message, state: FSMContext):
    await message.answer("В каком городе будем смотреть погоду? Напишите название.")
    
    await state.set_state(WeatherStates.waiting_for_city)

@router.message(WeatherStates.waiting_for_city, F.text)
async def process_city_name(message: Message, state: FSMContext):
    city_name = message.text.strip()
    
    await message.answer(f"Принято! Делаю запрос по городу: {city_name}...")

    weather_data = await get_weather_by_city(city_name)

    if weather_data:
        text = (
            f"Погода в городе {city_name}:\n"
            f"🌡 Температура: {weather_data['temp']}°C (ощущается как {weather_data['feels_like']}°C)\n"
            f"☁️ На улице: {weather_data['description']}"
        )
        await message.answer(text)
    else:
        await message.answer("Увы, такой город не найден или сервис временно недоступен. Попробуйте еще раз: /weather")
    
    await state.clear()

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    saved_path = await save_user_photo(message, bot)
    
    await message.answer(
        f"Фотография успешно сохранена.\n"
        f"Путь на сервере: {saved_path}"
    )

@router.message(Command("voice"))
async def handle_voice_command(message: Message):
    voice_path = FILES.voice_dir / "_ Alt.ogg"
    
    if not voice_path.exists():
        await message.answer("Файл голосового сообщения не найден на сервере.")
        return
        
    voice_file = FSInputFile(path=voice_path)
    await message.answer_voice(
        voice=voice_file, 
        caption="Ваше голосовое сообщение"
    )

@router.message(Command("translate"))
async def cmd_translate_start(message: Message, state: FSMContext):
    await message.answer("Отправьте текст, который нужно перевести на английский язык:")

    await state.set_state(TranslationFSM.waiting_for_text)

@router.message(StateFilter(TranslationFSM.waiting_for_text), F.text)
async def process_translation_text(message: Message, state: FSMContext):
    translated_text = await translate_text(message.text)
    
    await message.answer(f"🇬🇧 Перевод:\n{translated_text}")
    
    await state.clear()

@router.message(Command("register"))    
async def cmd_register_start(message: Message, state: FSMContext):
    student = await get_student_or_none(message.from_user.id)

    if student:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
            [    
            InlineKeyboardButton(text="👀 Посмотреть данные", callback_data="profile_view"),
            InlineKeyboardButton(text="✏️ Обновить данные", callback_data="profile_update")
            ]    
            ]
        )
        await message.answer(text="Вы уже зарегистрированы. Выберите действие", reply_markup=keyboard)
    else:
        await message.answer(text="Создание записи. Введите ваше имя:")
        await state.set_state(RegistrationFSM.waiting_for_name)  

@router.callback_query(F.data == "profile_view")
async def process_profile_view(callback: CallbackQuery):
    student = await get_student_or_none(callback.from_user.id)

    if student:
        text = (
            f"📋 <b>Ваша анкета:</b>\n\n"
            f"Имя: {student.name}\n"
            f"Возраст: {student.age}\n"
            f"Класс: {student.grade}"
        )

        await callback.message.edit_text(text, parse_mode="HTML")
    else:
        await callback.message.edit_text("⚠️ Запись не найдена")  

    await callback.answer()

@router.callback_query(F.data == "profile_update")    
async def process_profile_update(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Запускаем обновление. Введите свое имя")
    await state.set_state(RegistrationFSM.waiting_for_name)
    await callback.answer()

@router.message(StateFilter(RegistrationFSM.waiting_for_name), F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    await message.answer("Отлично. Теперь напиши свой возраст (только цифрой, например: 15):")
    await state.set_state(RegistrationFSM.waiting_for_age)

@router.message(StateFilter(RegistrationFSM.waiting_for_age), F.text)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом. Попробуй еще раз:")
        return
        
    await state.update_data(age=int(message.text))
    
    await message.answer("И последнее: в каком ты классе?")
    await state.set_state(RegistrationFSM.waiting_for_grade)

@router.message(StateFilter(RegistrationFSM.waiting_for_grade), F.text)
async def process_grade(message: Message, state: FSMContext):
    grade = message.text.strip()
    
    user_data = await state.get_data()
    
    await save_student(
        user_id=message.from_user.id,
        name=user_data['name'],
        age=user_data['age'],
        grade=grade
    )
    
    await message.answer(
        f"✅ Запись успешно сохранена!\n\n"
        f"Имя: {user_data['name']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Класс: {grade}"
    )
    
    await state.clear()
