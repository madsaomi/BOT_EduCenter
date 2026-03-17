import logging

logger = logging.getLogger(__name__)

# Mocked Data
COURSES = {
    1: {"id": 1, "title": "Python dasturlash", "price": "1,200,000 so'm", "duration": "3 oy"},
    2: {"id": 2, "title": "Web Developer (HTML/CSS/JS)", "price": "1,500,000 so'm", "duration": "4 oy"},
    3: {"id": 3, "title": "IELTS tayyorlov", "price": "800,000 so'm", "duration": "2 oy"},
    4: {"id": 4, "title": "English (boshlang'ich)", "price": "600,000 so'm", "duration": "2 oy"},
}

STUDENTS = {}

def init_db():
    logger.info("Demo Ma'lumotlar bazasi (Xotirada) tayyor SUCCESS")

# ── Kurslar ──────────────────────────────────────────────────────────────────

def get_all_courses():
    return list(COURSES.values())

def get_course(course_id: int):
    return COURSES.get(course_id)

# ── Talabalar ────────────────────────────────────────────────────────────────

def save_student(telegram_id: int, full_name: str, phone: str, course_id: int):
    STUDENTS[telegram_id] = {
        "telegram_id": telegram_id,
        "full_name": full_name,
        "phone": phone,
        "course_id": course_id,
    }

def get_all_students():
    result = []
    for telegram_id, student in STUDENTS.items():
        course = COURSES.get(student["course_id"])
        course_title = course["title"] if course else "Umumiy so'rov"
        result.append({
            "telegram_id": student["telegram_id"],
            "full_name": student["full_name"],
            "phone": student["phone"],
            "course_id": student["course_id"],
            "course_title": course_title
        })
    return result

def get_student(telegram_id: int):
    return STUDENTS.get(telegram_id)
