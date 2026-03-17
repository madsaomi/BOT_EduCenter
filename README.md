# 🤖 EduCenter — Telegram Bot

O'quv markazi uchun Aiogram Telegram bot.

## Ishga tushirish

`.env` faylga yozing:
```
BOT_TOKEN=your_token_here
ADMIN_ID=your_telegram_id
```

```bash
pip install -r requirements.txt
python main.py
```

## Bot buyruqlari

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish |
| `/courses` | Kurslar ro'yxati |
| `/help` | Yordam |
| `/admin` | Admin panel |
| `/students` | O'quvchilar ro'yxati |
| `/broadcast` | Barchaga xabar |

## Fayllar

- `main.py` — botni ishga tushirish
- `database.py` — SQLite bilan ishlash
- `handlers/` — foydalanuvchi va admin handlerlari
- `keyboards/` — reply va inline tugmalar
- `states/` — FSM holatlari (ro'yxatdan o'tish)
- `requirements.txt` — kutubxonalar
