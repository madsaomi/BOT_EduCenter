from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ── Reply keyboards ──────────────────────────────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Kurslar"), KeyboardButton(text="📝 Ro'yxatdan o'tish")],
            [KeyboardButton(text="👤 Mening ma'lumotlarim"), KeyboardButton(text="☎️ Aloqa")],
        ],
        resize_keyboard=True,
    )


def contact_kb() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish uchun."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


# ── Inline keyboards ─────────────────────────────────────────────────────────

def courses_inline_kb(courses) -> InlineKeyboardMarkup:
    """Kurslar ro'yxati inline button sifatida."""
    builder = InlineKeyboardBuilder()
    for course in courses:
        builder.button(
            text=f"📖 {course['title']} – {course['price']}",
            callback_data=f"course_{course['id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm_no"),
        ]
    ])
