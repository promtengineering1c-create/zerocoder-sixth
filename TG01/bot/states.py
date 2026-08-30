from aiogram.fsm.state import State, StatesGroup


class TranslationFSM(StatesGroup):
    waiting_for_text = State()