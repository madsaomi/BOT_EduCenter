import sqlite3
import logging
import os
import sys

# Remove sys.path hack that confuses IDE
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database sozlamalari
DB_NAME = os.getenv("DB_NAME", "instance/edu_center_bot.db")

logger = logging.getLogger(__name__)


def get_connection():
    # Resolve the database path relative to the project root (one level up from project2_bot)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создание таблиц при первом запуске."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT NOT NULL,
            price    TEXT NOT NULL,
            duration TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name   TEXT NOT NULL,
            phone       TEXT NOT NULL,
            course_id   INTEGER,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)

    # Demo kurslar (agar bo'sh bo'lsa)
    count = cur.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count == 0:
        demo_courses = [
            ("Python dasturlash",      "1,200,000 so'm", "3 oy"),
            ("Web Developer (HTML/CSS/JS)", "1,500,000 so'm", "4 oy"),
            ("IELTS tayyorlov",         "800,000 so'm",  "2 oy"),
            ("English (boshlang'ich)",  "600,000 so'm",  "2 oy"),
        ]
        cur.executemany(
            "INSERT INTO courses (title, price, duration) VALUES (?, ?, ?)",
            demo_courses,
        )
        logger.info("Demo kurslar yaratildi")

    conn.commit()
    conn.close()
    logger.info("Ma'lumotlar bazasi tayyor SUCCESS")


# ── Kurslar ──────────────────────────────────────────────────────────────────

def get_all_courses():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM courses").fetchall()


def get_course(course_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()


# ── Talabalar ────────────────────────────────────────────────────────────────

def save_student(telegram_id: int, full_name: str, phone: str, course_id: int):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO students (telegram_id, full_name, phone, course_id)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(telegram_id) DO UPDATE SET
                   full_name=excluded.full_name,
                   phone=excluded.phone,
                   course_id=excluded.course_id,
                   created_at=CURRENT_TIMESTAMP""",
            (telegram_id, full_name, phone, course_id),
        )
        conn.commit()


def get_all_students():
    with get_connection() as conn:
        return conn.execute("""
            SELECT s.*, c.title as course_title
            FROM students s
            LEFT JOIN courses c ON s.course_id = c.id
            ORDER BY s.created_at DESC
        """).fetchall()


def get_student(telegram_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
