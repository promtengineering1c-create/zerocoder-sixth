from aiogram.fsm.state import State, StatesGroup


class WeatherStates(StatesGroup):
    waiting_for_city = State()