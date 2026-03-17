import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import sys
import os
# Bot root ni qo'shish (keyboards, database va hklar uchun)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_all_courses, get_course, save_student, get_student
from keyboards.keyboards import (
    main_menu_kb, contact_kb, cancel_kb,
    courses_inline_kb, confirm_kb,
)
from states.states import RegistrationFSM

logger = logging.getLogger(__name__)
router = Router()


# ── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    student = get_student(message.from_user.id)
    if student:
        await message.answer(
            f"👋 Qaytib keldingiz, <b>{student['full_name']}</b>!\n"
            f"Quyidagi menyudan foydalaning:",
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer(
            "🎓 <b>EduCenter botiga xush kelibsiz!</b>\n\n"
            "Bu bot orqali siz:\n"
            "📚 Kurslar bilan tanishishingiz\n"
            "📝 Ro'yxatdan o'tishingiz\n"
            "☎️ Biz bilan bog'lanishingiz mumkin.\n\n"
            "Quyidagi menyudan tanlang 👇",
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )


# ── /help ────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📌 <b>Yordam</b>\n\n"
        "/start – Botni qayta ishga tushirish\n"
        "/courses – Kurslar ro'yxati\n"
        "/help – Yordam\n\n"
        "Muammo bo'lsa: <b>+998 90 000 00 00</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ── /courses ─────────────────────────────────────────────────────────────────

@router.message(Command("courses"))
@router.message(F.text == "📚 Kurslar")
async def show_courses(message: Message):
    courses = get_all_courses()
    if not courses:
        await message.answer("😔 Hozircha kurslar mavjud emas.")
        return
    await message.answer(
        "📚 <b>Mavjud kurslar:</b>\n\nKurs tanlash uchun tugmani bosing 👇",
        parse_mode="HTML",
        reply_markup=courses_inline_kb(courses),
    )


# ── Kurs detail ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("course_"))
async def course_detail(callback: CallbackQuery):
    course_id = int(callback.data.split("_")[1])
    course = get_course(course_id)
    if not course:
        await callback.answer("Kurs topilmadi", show_alert=True)
        return
    await callback.message.answer(
        f"📖 <b>{course['title']}</b>\n\n"
        f"💰 Narxi: <b>{course['price']}</b>\n"
        f"⏱ Davomiyligi: <b>{course['duration']}</b>\n\n"
        f"Ushbu kursga yozilmoqchimisiz?",
        parse_mode="HTML",
        reply_markup=courses_inline_kb(get_all_courses()),
    )
    await callback.answer()


# ── Ro'yxatdan o'tish ────────────────────────────────────────────────────────

@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_registration(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegistrationFSM.waiting_name)
    await message.answer(
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "1️⃣ Ism va familiyangizni kiriting:\n"
        "<i>Masalan: Ali Valiyev</i>",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )


@router.message(RegistrationFSM.waiting_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.", reply_markup=main_menu_kb())
        return

    name = message.text.strip()
    if len(name) < 3 or len(name) > 100:
        await message.answer("⚠️ Ism kamida 3 ta harf bo'lishi kerak. Qaytadan kiriting:")
        return

    await state.update_data(full_name=name)
    await state.set_state(RegistrationFSM.waiting_phone)
    await message.answer(
        f"✅ <b>{name}</b>\n\n"
        "2️⃣ Telefon raqamingizni kiriting yoki tugmani bosing:\n"
        "<i>Masalan: +998901234567</i>",
        parse_mode="HTML",
        reply_markup=contact_kb(),
    )


@router.message(RegistrationFSM.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await _phone_received(message, state, phone)


@router.message(RegistrationFSM.waiting_phone)
async def process_phone_text(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())
        return
    if message.text == "⬅️ Orqaga":
        await state.set_state(RegistrationFSM.waiting_name)
        await message.answer("Ismingizni qaytadan kiriting:", reply_markup=cancel_kb())
        return

    phone = message.text.strip().replace(" ", "").replace("-", "")
    if len(phone) < 9:
        await message.answer("⚠️ Telefon raqam noto'g'ri formatda. Qaytadan kiriting:")
        return

    await _phone_received(message, state, phone)


async def _phone_received(message: Message, state: FSMContext, phone: str):
    await state.update_data(phone=phone)
    await state.set_state(RegistrationFSM.waiting_course)
    courses = get_all_courses()
    await message.answer(
        f"✅ Telefon: <b>{phone}</b>\n\n"
        "3️⃣ Qaysi kursga yozilmoqchisiz? 👇",
        parse_mode="HTML",
        reply_markup=courses_inline_kb(courses),
    )


@router.callback_query(RegistrationFSM.waiting_course, F.data.startswith("course_"))
async def process_course_choice(callback: CallbackQuery, state: FSMContext):
    course_id = int(callback.data.split("_")[1])
    course = get_course(course_id)
    if not course:
        await callback.answer("Kurs topilmadi!", show_alert=True)
        return

    await state.update_data(course_id=course_id, course_title=course["title"])
    await state.set_state(RegistrationFSM.confirm)

    data = await state.get_data()
    await callback.message.answer(
        "📋 <b>Ma'lumotlarni tekshiring:</b>\n\n"
        f"👤 Ism: <b>{data['full_name']}</b>\n"
        f"📱 Telefon: <b>{data['phone']}</b>\n"
        f"📖 Kurs: <b>{data['course_title']}</b>\n"
        f"💰 Narxi: <b>{course['price']}</b>\n\n"
        "Tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=confirm_kb(),
    )
    await callback.answer()


@router.callback_query(RegistrationFSM.confirm, F.data == "confirm_yes")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    save_student(
        telegram_id=callback.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        course_id=data["course_id"],
    )
    await state.clear()
    await callback.message.answer(
        "🎉 <b>Muvaffaqiyatli ro'yxatdan o'tdingiz!</b>\n\n"
        f"📖 Kurs: <b>{data['course_title']}</b>\n\n"
        "✅ Tez orada administratorimiz siz bilan bog'lanadi.",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )

    # Adminga xabar yuborish (main.py orqali bot orqali)
    import os
    ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))
    from aiogram import Bot
    bot: Bot = callback.bot
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 <b>Yangi ariza!</b>\n\n"
            f"👤 Ism: {data['full_name']}\n"
            f"📱 Telefon: {data['phone']}\n"
            f"📖 Kurs: {data['course_title']}\n"
            f"🆔 Telegram ID: {callback.from_user.id}",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning(f"Admin ga xabar yuborib bo'lmadi: {e}")

    await callback.answer()


@router.callback_query(RegistrationFSM.confirm, F.data == "confirm_no")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Ro'yxatdan o'tish bekor qilindi.\n"
        "Xohlasangiz qaytadan urinib ko'ring 👇",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ── Mening ma'lumotlarim ─────────────────────────────────────────────────────

@router.message(F.text == "👤 Mening ma'lumotlarim")
async def my_info(message: Message):
    student = get_student(message.from_user.id)
    if not student:
        await message.answer(
            "😔 Siz hali ro'yxatdan o'tmagansiz.\n"
            "📝 Ro'yxatdan o'tish tugmasini bosing.",
            reply_markup=main_menu_kb(),
        )
        return

    course = get_course(student["course_id"]) if student["course_id"] else None
    course_title = course["title"] if course else "Kurs tanlanmagan"

    await message.answer(
        f"👤 <b>Sizning ma'lumotlaringiz:</b>\n\n"
        f"📛 Ism: <b>{student['full_name']}</b>\n"
        f"📱 Telefon: <b>{student['phone']}</b>\n"
        f"📖 Kurs: <b>{course_title}</b>\n"
        f"📅 Ro'yxatdan o'tgan: <b>{student['created_at'][:10]}</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ── Aloqa ────────────────────────────────────────────────────────────────────

@router.message(F.text == "☎️ Aloqa")
async def contact_info(message: Message):
    await message.answer(
        "☎️ <b>Biz bilan bog'laning:</b>\n\n"
        "📞 Telefon: <b>+998 90 000 00 00</b>\n"
        "📍 Manzil: Toshkent sh., Chilonzor tumani\n"
        "🕐 Ish vaqti: Du–Sha, 09:00–18:00\n"
        "📱 Telegram: @edu_center_uz",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
