from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from config.settings.base import FILES
from weather_api.client import get_weather_by_city
from weather_api.states import WeatherStates

from .services.files import save_user_photo
from .services.translator import translate_text
from config.settings.base import FILES
from .states import TranslationFSM

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
     