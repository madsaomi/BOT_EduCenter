from aiogram.fsm.state import State, StatesGroup


class RegistrationFSM(StatesGroup):
    waiting_name   = State()   # Ism kiritish
    waiting_phone  = State()   # Telefon raqam
    waiting_course = State()   # Kurs tanlash
    confirm        = State()   # Tasdiqlash
