from aiogram.fsm.state import State, StatesGroup


class TranslationFSM(StatesGroup):
    waiting_for_text = State()

class RegistrationFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_grade = State()