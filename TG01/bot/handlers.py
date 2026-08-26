from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from weather_api.client import get_weather_by_city
from weather_api.states import WeatherStates

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

@router.message(WeatherStates.waiting_for_city)
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