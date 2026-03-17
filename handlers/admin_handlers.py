import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import sys
import os
# Bot root ni qo'shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))
from database import get_all_students, get_all_courses

logger = logging.getLogger(__name__)
router = Router()


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# ── /admin ───────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message):
        await message.answer("⛔ Sizda admin huquqi yo'q.")
        return

    students = get_all_students()
    courses = get_all_courses()

    builder = InlineKeyboardBuilder()
    builder.button(text="👥 O'quvchilar ro'yxati", callback_data="admin_students")
    builder.button(text="📚 Kurslar statistikasi", callback_data="admin_courses_stat")
    builder.adjust(1)

    await message.answer(
        f"⚙️ <b>Admin Panel</b>\n\n"
        f"👥 Jami o'quvchilar: <b>{len(students)}</b>\n"
        f"📚 Kurslar soni: <b>{len(courses)}</b>",
        parse_mode="HTML",
        reply_markup=builder.as_markup(),
    )


# ── Admin students list ───────────────────────────────────────────────────────

@router.message(Command("students"))
async def list_students(message: Message):
    if not is_admin(message):
        await message.answer("⛔ Ruxsat yo'q.")
        return

    students = get_all_students()
    if not students:
        await message.answer("📭 Hozircha ro'yxatdan o'tgan o'quvchilar yo'q.")
        return

    # Xabarni bo'laklarga bo'lib yuborish (Telegram 4096 limit)
    text = "👥 <b>O'quvchilar ro'yxati:</b>\n\n"
    chunks = []
    for i, s in enumerate(students, 1):
        course_title = s['course_title'] or "Kurs yo'q"
        line = (
            f"{i}. <b>{s['full_name']}</b>\n"
            f"   📱 {s['phone']}\n"
            f"   📖 {course_title}\n"
            f"   🆔 {s['telegram_id']}\n\n"
        )
        if len(text) + len(line) > 4000:
            chunks.append(text)
            text = ""
        text += line

    if text:
        chunks.append(text)

    for chunk in chunks:
        await message.answer(chunk, parse_mode="HTML")


# ── Broadcast ────────────────────────────────────────────────────────────────

@router.message(Command("broadcast"))
async def broadcast(message: Message):
    """Barcha o'quvchilarga xabar yuborish.
    Ishlatish: /broadcast Xabar matni shu yerga
    """
    if not is_admin(message):
        await message.answer("⛔ Ruxsat yo'q.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "ℹ️ Ishlatish:\n<code>/broadcast Xabar matni</code>",
            parse_mode="HTML",
        )
        return

    broadcast_text = parts[1]
    students = get_all_students()

    if not students:
        await message.answer("📭 Xabar yuborish uchun o'quvchilar yo'q.")
        return

    sent = 0
    failed = 0
    for student in students:
        try:
            await message.bot.send_message(
                student["telegram_id"],
                f"📢 <b>EduCenter xabari:</b>\n\n{broadcast_text}",
                parse_mode="HTML",
            )
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning(f"ID {student['telegram_id']} ga yuborib bo'lmadi: {e}")

    await message.answer(
        f"✅ Xabar yuborildi:\n"
        f"📤 Muvaffaqiyatli: <b>{sent}</b>\n"
        f"❌ Yuborib bo'lmadi: <b>{failed}</b>",
        parse_mode="HTML",
    )


# ── Inline callback handlers ──────────────────────────────────────────────────

from aiogram.types import CallbackQuery


@router.callback_query(F.data == "admin_students")
async def cb_admin_students(callback: CallbackQuery):
    if not is_admin(callback.message):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    students = get_all_students()
    if not students:
        await callback.message.answer("📭 Hozircha o'quvchilar yo'q.")
        await callback.answer()
        return

    text = "👥 <b>O'quvchilar:</b>\n\n"
    for i, s in enumerate(students[:20], 1):
        text += f"{i}. <b>{s['full_name']}</b> – {s['phone']} – {s['course_title'] or '—'}\n"

    if len(students) > 20:
        text += f"\n<i>...va yana {len(students) - 20} nafar</i>"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_courses_stat")
async def cb_admin_courses_stat(callback: CallbackQuery):
    courses = get_all_courses()
    students = get_all_students()

    text = "📊 <b>Kurslar statistikasi:</b>\n\n"
    for course in courses:
        count = sum(1 for s in students if s["course_id"] == course["id"])
        text += f"📖 <b>{course['title']}</b>: {count} o'quvchi\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
