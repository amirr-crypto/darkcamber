import telebot
from telebot import types
import sqlite3
import time
import random
from datetime import datetime, date


# =========================================================
# TOKEN
# =========================================================

TOKEN = "8507151803:AAHTYb84d2HlAh6jDbFYJZs5hUmVAJLM99s"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8820677197
DB_FILE = "darkcamper.db"


# =========================================================
# KANALLAR
# =========================================================

CHANNELS = [
    {
        "name": "📱 Manipulatsiya",
        "username": "@manipulator_liders"
    },
    {
        "name": "📰 Yangiliklar",
        "username": "@google_todaynews"
    },
    {
        "name": "📈 Trading",
        "username": "@AROpro_fx"
    },
    {
        "name": "🆘 Yordam",
        "username": "@amirr_khakimoff"
    },
    {
        "name": "💻 Lider",
        "username": "@Y5K8A7"
    },
    {
        "name": "📖 Ma'lumotnoma",
        "username": "@darkcamper_information"
    }
]


# =========================================================
# KURSLAR
# =========================================================

COURSES = {
    "smm": {
        "name": "📱 SMM",
        "lessons": [
            "SMM asoslari",
            "Auditoriyani aniqlash",
            "Kontent strategiyasi",
            "Instagram algoritmi",
            "Reels strategiyasi",
            "Copywriting asoslari",
            "Brend yaratish",
            "Target reklama",
            "Analitika",
            "SMM strategiyasi"
        ]
    },

    "trading": {
        "name": "📈 Trading",
        "lessons": [
            "Trading asoslari",
            "Grafikni tushunish",
            "Support va Resistance",
            "Trendlar",
            "Candlestick asoslari",
            "Risk Management",
            "Stop Loss",
            "Take Profit",
            "Strategiya",
            "Trading psixologiyasi"
        ]
    },

    "programming": {
        "name": "💻 Programming",
        "lessons": [
            "Programming nima?",
            "Python asoslari",
            "O'zgaruvchilar",
            "Shart operatorlari",
            "Looplar",
            "Funksiyalar",
            "List va Dictionary",
            "Telegram bot asoslari",
            "Database",
            "Professional loyiha"
        ]
    }
}


# =========================================================
# MOTIVATSIYALAR
# =========================================================

MOTIVATIONS = [
    "🔥 Har kuni kichik qadam — katta natijaga olib boradi.",
    "🧠 Bilimga investitsiya qilish — eng kuchli investitsiya.",
    "🎯 Maqsad aniq bo'lsa, yo'l ham topiladi.",
    "🚀 Boshlash uchun mukammal vaqtni kutma.",
    "💡 O'rgan, sinab ko'r, xato qil va yana davom et.",
    "🏆 Kuchli natijalar kuchli intizomdan boshlanadi.",
    "⚡ Bugungi harakating ertangi imkoniyatingni yaratadi."
]


# =========================================================
# DATABASE
# =========================================================

def get_db():
    return sqlite3.connect(DB_FILE)


def init_db():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            joined_date TEXT,
            last_active TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            last_streak_date TEXT,
            referrals INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            course TEXT,
            lesson INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, course)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            user_id INTEGER,
            task_date TEXT,
            completed INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, task_date)
        )
    """)

    db.commit()
    db.close()


init_db()


# =========================================================
# USERNI BAZAGA SAQLASH
# =========================================================

def save_user(user, referral_id=0):

    db = get_db()
    cursor = db.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user.id,)
    )

    exists = cursor.fetchone()

    if not exists:

        first_name = user.first_name or "Noma'lum"
        username = user.username or ""

        referred_by = 0

        if referral_id:
            if referral_id != user.id:

                cursor.execute(
                    "SELECT user_id FROM users WHERE user_id = ?",
                    (referral_id,)
                )

                ref_exists = cursor.fetchone()

                if ref_exists:
                    referred_by = referral_id

                    cursor.execute("""
                        UPDATE users
                        SET referrals = referrals + 1,
                            xp = xp + 50
                        WHERE user_id = ?
                    """, (referral_id,))

        cursor.execute("""
            INSERT INTO users
            (
                user_id,
                first_name,
                username,
                joined_date,
                last_active,
                xp,
                level,
                streak,
                last_streak_date,
                referrals,
                referred_by,
                blocked
            )
            VALUES (?, ?, ?, ?, ?, 0, 1, 0, '', 0, ?, 0)
        """, (
            user.id,
            first_name,
            username,
            now,
            now,
            referred_by
        ))

    else:

        cursor.execute("""
            UPDATE users
            SET first_name = ?,
                username = ?,
                last_active = ?
            WHERE user_id = ?
        """, (
            user.first_name or "Noma'lum",
            user.username or "",
            now,
            user.id
        ))

    db.commit()
    db.close()


# =========================================================
# USER MA'LUMOTI
# =========================================================

def get_user(user_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            first_name,
            username,
            joined_date,
            last_active,
            xp,
            level,
            streak,
            last_streak_date,
            referrals,
            referred_by,
            blocked
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    db.close()

    return result


# =========================================================
# XP QO'SHISH
# =========================================================

def add_xp(user_id, amount):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET xp = xp + ?
        WHERE user_id = ?
    """, (amount, user_id))

    cursor.execute("""
        SELECT xp, level
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if result:

        xp = result[0]
        level = max(1, (xp // 100) + 1)

        cursor.execute("""
            UPDATE users
            SET level = ?
            WHERE user_id = ?
        """, (level, user_id))

    db.commit()
    db.close()


# =========================================================
# STREAK
# =========================================================

def update_streak(user_id):

    db = get_db()
    cursor = db.cursor()

    today = date.today()

    cursor.execute("""
        SELECT streak, last_streak_date
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if not result:
        db.close()
        return

    streak = result[0]
    last_date = result[1]

    if last_date == str(today):
        db.close()
        return

    if last_date:

        try:

            old_date = datetime.strptime(
                last_date,
                "%Y-%m-%d"
            ).date()

            difference = (today - old_date).days

            if difference == 1:
                streak += 1
            else:
                streak = 1

        except:
            streak = 1

    else:
        streak = 1

    cursor.execute("""
        UPDATE users
        SET streak = ?,
            last_streak_date = ?
        WHERE user_id = ?
    """, (
        streak,
        str(today),
        user_id
    ))

    db.commit()
    db.close()

    add_xp(user_id, 5)


# =========================================================
# BLOCK TEKSHIRISH
# =========================================================

def is_blocked(user_id):

    user = get_user(user_id)

    if user:
        return user[11] == 1

    return False


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_menu():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "📱 Manipulatsiya",
            url="https://t.me/manipulator_liders"
        ),
        types.InlineKeyboardButton(
            "📰 Yangiliklar",
            url="https://t.me/google_todaynews"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📈 Trading",
            url="https://t.me/AROpro_fx"
        ),
        types.InlineKeyboardButton(
            "🆘 Yordam",
            url="https://t.me/amirr_khakimoff"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "💻 Lider",
            url="https://t.me/Y5K8A7"
        ),
        types.InlineKeyboardButton(
            "📖 Ma'lumotnoma",
            url="https://t.me/darkcamper_information"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "👤 Profil",
            callback_data="profile"
        ),
        types.InlineKeyboardButton(
            "🎓 Academy",
            callback_data="academy"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "🏆 Reyting",
            callback_data="rating"
        ),
        types.InlineKeyboardButton(
            "🎯 Vazifa",
            callback_data="daily"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "💬 Feedback",
            callback_data="feedback"
        ),
        types.InlineKeyboardButton(
            "🔗 Referal",
            callback_data="referral"
        )
    )

    return keyboard


# =========================================================
# ADMIN MENU
# =========================================================

def admin_menu():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "👥 Foydalanuvchilar",
            callback_data="users"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📊 Statistika",
            callback_data="stats"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📢 Broadcast",
            callback_data="broadcast"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "🔎 User qidirish",
            callback_data="search_user"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "💬 Feedbacklar",
            callback_data="feedbacks"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "🔙 Asosiy menyu",
            callback_data="home"
        )
    )

    return keyboard


# =========================================================
# ACADEMY MENU
# =========================================================

def academy_menu():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "📱 SMM",
            callback_data="course:smm"
        ),
        types.InlineKeyboardButton(
            "📈 Trading",
            callback_data="course:trading"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "💻 Programming",
            callback_data="course:programming"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="home"
        )
    )

    return keyboard


# =========================================================
# KURS MENYU
# =========================================================

def course_menu(course):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "▶️ Darsni davom ettirish",
            callback_data=f"lesson:{course}"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📚 Barcha darslar",
            callback_data=f"lessons:{course}"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "🔙 Academy",
            callback_data="academy"
        )
    )

    return keyboard


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    referral_id = 0

    try:

        parts = message.text.split()

        if len(parts) > 1:
            referral_id = int(parts[1])

    except:
        referral_id = 0

    save_user(
        message.from_user,
        referral_id
    )

    if is_blocked(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "🚫 Siz botdan foydalanish huquqidan mahrum qilingansiz."
        )

        return

    update_streak(message.from_user.id)

    bot.send_message(
        message.chat.id,

        f"""
🔥 <b>DARKCAMPER</b>

Salom, {message.from_user.first_name}! 👋

🚀 Bu yerda siz:

📱 SMM
📈 Trading
💻 Programming
🧠 Liderlik
📰 Yangiliklar

va boshqa foydali bo'limlardan foydalanishingiz mumkin.

🎓 Academy orqali bilim o'rganing.
🏆 XP yig'ing.
🔥 Streakni saqlang.
🎯 Kunlik vazifalarni bajaring.

Kerakli bo'limni tanlang 👇
""",

        parse_mode="HTML",
        reply_markup=main_menu()
    )


# =========================================================
# ADMIN
# =========================================================

@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id != ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "❌ Siz admin emassiz."
        )

        return

    bot.send_message(
        message.chat.id,
        "👑 <b>DARKCAMPER ADMIN PANEL</b>",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# =========================================================
# CALLBACKLAR
# =========================================================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    bot.answer_callback_query(call.id)

    user_id = call.from_user.id

    if is_blocked(user_id):

        bot.send_message(
            call.message.chat.id,
            "🚫 Siz bloklangansiz."
        )

        return


    # =====================================================
    # HOME
    # =====================================================

    if call.data == "home":

        bot.send_message(
            call.message.chat.id,
            "🏠 Asosiy menyu:",
            reply_markup=main_menu()
        )


    # =====================================================
    # PROFILE
    # =====================================================

    elif call.data == "profile":

        user = get_user(user_id)

        if not user:
            save_user(call.from_user)
            user = get_user(user_id)

        username = user[2]

        if username:
            username_text = "@" + username
        else:
            username_text = "Username yo'q"

        bot.send_message(
            call.message.chat.id,

            f"""
👤 <b>SIZNING PROFILINGIZ</b>

👤 Ism: {user[1]}
🔗 Username: {username_text}
🆔 ID: <code>{user[0]}</code>

⭐ XP: {user[5]}
🏅 Daraja: {user[6]}
🔥 Streak: {user[7]} kun
👥 Referallar: {user[9]}

📅 Ro'yxatdan o'tgan:
{user[3]}

🚀 DARKCAMPER USER
""",

            parse_mode="HTML"
        )


    # =====================================================
    # ACADEMY
    # =====================================================

    elif call.data == "academy":

        bot.send_message(
            call.message.chat.id,
            """
🎓 <b>DARKCAMPER ACADEMY</b>

Bilim olish uchun kursni tanlang 👇
""",
            parse_mode="HTML",
            reply_markup=academy_menu()
        )


    # =====================================================
    # COURSE
    # =====================================================

    elif call.data.startswith("course:"):

        course = call.data.split(":", 1)[1]

        if course not in COURSES:
            return

        data = COURSES[course]

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT lesson
            FROM progress
            WHERE user_id = ? AND course = ?
        """, (user_id, course))

        result = cursor.fetchone()

        db.close()

        current = result[0] if result else 0

        total = len(data["lessons"])

        bot.send_message(
            call.message.chat.id,

            f"""
🎓 <b>{data['name']} KURSI</b>

📚 Darslar: {total}
✅ Tugatilgan: {current}
📊 Progress: {current}/{total}

O'qishni davom ettiring 👇
""",

            parse_mode="HTML",
            reply_markup=course_menu(course)
        )


    # =====================================================
    # LESSONS
    # =====================================================

    elif call.data.startswith("lessons:"):

        course = call.data.split(":", 1)[1]

        if course not in COURSES:
            return

        text = f"📚 <b>{COURSES[course]['name']} Darslari</b>\n\n"

        for i, lesson in enumerate(
            COURSES[course]["lessons"],
            start=1
        ):

            text += f"{i}. {lesson}\n"

        keyboard = types.InlineKeyboardMarkup()

        keyboard.row(
            types.InlineKeyboardButton(
                "▶️ Boshlash",
                callback_data=f"lesson:{course}"
            )
        )

        keyboard.row(
            types.InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data=f"course:{course}"
            )
        )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # LESSON
    # =====================================================

    elif call.data.startswith("lesson:"):

        course = call.data.split(":", 1)[1]

        if course not in COURSES:
            return

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT lesson
            FROM progress
            WHERE user_id = ? AND course = ?
        """, (user_id, course))

        result = cursor.fetchone()

        current = result[0] if result else 0

        db.close()

        lessons = COURSES[course]["lessons"]

        if current >= len(lessons):

            bot.send_message(
                call.message.chat.id,
                "🏆 Siz bu kursni to'liq tugatgansiz!"
            )

            return

        lesson_number = current + 1
        lesson_name = lessons[current]

        keyboard = types.InlineKeyboardMarkup()

        keyboard.row(
            types.InlineKeyboardButton(
                "✅ Darsni tugatdim",
                callback_data=f"complete:{course}"
            )
        )

        keyboard.row(
            types.InlineKeyboardButton(
                "🔙 Kurs",
                callback_data=f"course:{course}"
            )
        )

        bot.send_message(
            call.message.chat.id,

            f"""
📚 <b>{COURSES[course]['name']}</b>

🔢 Dars {lesson_number}/{len(lessons)}

🎯 <b>{lesson_name}</b>

Bu darsni o'rganing va tugatganingizdan keyin
pastdagi tugmani bosing.

⭐ Mukofot: +20 XP
""",

            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # COMPLETE LESSON
    # =====================================================

    elif call.data.startswith("complete:"):

        course = call.data.split(":", 1)[1]

        if course not in COURSES:
            return

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT lesson
            FROM progress
            WHERE user_id = ? AND course = ?
        """, (user_id, course))

        result = cursor.fetchone()

        current = result[0] if result else 0

        total = len(COURSES[course]["lessons"])

        if current < total:

            current += 1

            cursor.execute("""
                INSERT OR REPLACE INTO progress
                (user_id, course, lesson)
                VALUES (?, ?, ?)
            """, (
                user_id,
                course,
                current
            ))

            db.commit()

        db.close()

        add_xp(user_id, 20)

        if current >= total:

            text = """
🏆 <b>TABRIKLAYMIZ!</b>

Siz kursni to'liq tugatdingiz! 🎓

⭐ +20 XP
🏆 Yangi darajaga yaqinlashdingiz!
"""

        else:

            next_lesson = COURSES[course]["lessons"][current]

            text = f"""
✅ <b>DARS YAKUNLANDI!</b>

⭐ +20 XP

📚 Keyingi dars:
<b>{next_lesson}</b>

Davom eting! 🚀
"""

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=course_menu(course)
        )


    # =====================================================
    # RATING
    # =====================================================

    elif call.data == "rating":

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT first_name, username, xp, level
            FROM users
            WHERE blocked = 0
            ORDER BY xp DESC
            LIMIT 10
        """)

        users = cursor.fetchall()

        db.close()

        text = "🏆 <b>DARKCAMPER TOP 10</b>\n\n"

        medals = [
            "🥇",
            "🥈",
            "🥉"
        ]

        for index, user in enumerate(users, start=1):

            if index <= 3:
                prefix = medals[index - 1]
            else:
                prefix = f"{index}."

            text += (
                f"{prefix} "
                f"{user[0]} — "
                f"⭐ {user[2]} XP "
                f"| 🏅 {user[3]}\n"
            )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML"
        )


    # =====================================================
    # DAILY TASK
    # =====================================================

    elif call.data == "daily":

        today = str(date.today())

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT completed
            FROM tasks
            WHERE user_id = ? AND task_date = ?
        """, (user_id, today))

        result = cursor.fetchone()

        completed = result[0] if result else 0

        db.close()

        if completed:

            text = """
🎯 <b>BUGUNGI VAZIFA</b>

✅ Siz bugungi vazifani bajargansiz!

🔥 +10 XP olgansiz.
"""

            bot.send_message(
                call.message.chat.id,
                text,
                parse_mode="HTML"
            )

            return

        tasks = [
            "📚 15 daqiqa yangi bilim o'rganing.",
            "🧠 Bugun 5 ta yangi tushuncha yozib oling.",
            "🎯 Ertangi maqsadingizni yozib qo'ying.",
            "💻 20 daqiqa kod yozing.",
            "📱 SMM bo'yicha bitta yangi narsani o'rganing.",
            "📈 Trading bo'yicha bitta mavzuni o'rganing."
        ]

        task = random.choice(tasks)

        keyboard = types.InlineKeyboardMarkup()

        keyboard.row(
            types.InlineKeyboardButton(
                "✅ Bajardim",
                callback_data="task_done"
            )
        )

        bot.send_message(
            call.message.chat.id,

            f"""
🎯 <b>BUGUNGI TOPSHIRIQ</b>

{task}

Bajarganingizdan keyin tugmani bosing 👇

⭐ Mukofot: +10 XP
""",

            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # TASK DONE
    # =====================================================

    elif call.data == "task_done":

        today = str(date.today())

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT completed
            FROM tasks
            WHERE user_id = ? AND task_date = ?
        """, (user_id, today))

        result = cursor.fetchone()

        if result and result[0] == 1:

            db.close()

            bot.send_message(
                call.message.chat.id,
                "⚠️ Bugungi vazifa allaqachon bajarilgan."
            )

            return

        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (user_id, task_date, completed)
            VALUES (?, ?, 1)
        """, (
            user_id,
            today
        ))

        db.commit()
        db.close()

        add_xp(user_id, 10)

        bot.send_message(
            call.message.chat.id,

            """
🎉 <b>VAZIFA BAJARILDI!</b>

✅ +10 XP

🔥 Davom eting!
""",

            parse_mode="HTML"
        )


    # =====================================================
    # REFERRAL
    # =====================================================

    elif call.data == "referral":

        bot_username = bot.get_me().username

        link = (
            f"https://t.me/{bot_username}"
            f"?start={user_id}"
        )

        user = get_user(user_id)

        referrals = user[9] if user else 0

        bot.send_message(
            call.message.chat.id,

            f"""
🔗 <b>REFERAL TIZIMI</b>

Sizning shaxsiy havolangiz:

<code>{link}</code>

👥 Taklif qilganlaringiz: {referrals}

🎁 Har bir yangi foydalanuvchi uchun:
⭐ +50 XP

Havolani do'stlaringizga yuboring 🚀
""",

            parse_mode="HTML"
        )


    # =====================================================
    # FEEDBACK
    # =====================================================

    elif call.data == "feedback":

        msg = bot.send_message(
            call.message.chat.id,
            """
💬 <b>FEEDBACK</b>

Bot haqida fikringizni yozing 👇
""",
            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            receive_feedback
        )


    # =====================================================
    # ADMIN USERS
    # =====================================================

    elif call.data == "users":

        if user_id != ADMIN_ID:
            return

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT user_id, first_name, username, xp, level, blocked
            FROM users
            ORDER BY rowid DESC
            LIMIT 50
        """)

        users = cursor.fetchall()

        db.close()

        if not users:

            bot.send_message(
                call.message.chat.id,
                "👥 Foydalanuvchilar yo'q."
            )

            return

        keyboard = types.InlineKeyboardMarkup()

        for index, user in enumerate(users, start=1):

            name = user[1] or "Noma'lum"

            if len(name) > 20:
                name = name[:20]

            status = "🚫" if user[5] else "🟢"

            keyboard.row(
                types.InlineKeyboardButton(
                    f"{status} {index}. {name} | ⭐{user[3]}",
                    callback_data=f"user:{user[0]}"
                )
            )

        keyboard.row(
            types.InlineKeyboardButton(
                "🔙 Admin",
                callback_data="admin_home"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "👥 <b>FOYDALANUVCHILAR</b>\n\nOxirgi foydalanuvchilar:",
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # ADMIN USER PROFILE
    # =====================================================

    elif call.data.startswith("user:"):

        if user_id != ADMIN_ID:
            return

        target_id = int(
            call.data.split(":", 1)[1]
        )

        user = get_user(target_id)

        if not user:

            bot.send_message(
                call.message.chat.id,
                "❌ Foydalanuvchi topilmadi."
            )

            return

        username = (
            "@" + user[2]
            if user[2]
            else "Username yo'q"
        )

        status = (
            "🚫 BLOKLANGAN"
            if user[11]
            else "🟢 AKTIV"
        )

        text = f"""
👤 <b>FOYDALANUVCHI</b>

👤 Ism: {user[1]}
🔗 Username: {username}
🆔 ID: <code>{user[0]}</code>

⭐ XP: {user[5]}
🏅 Level: {user[6]}
🔥 Streak: {user[7]}
👥 Referral: {user[9]}

📅 Ro'yxatdan o'tgan:
{user[3]}

🕐 Oxirgi faollik:
{user[4]}

📌 Holat: {status}
"""

        keyboard = types.InlineKeyboardMarkup()

        if user[11]:

            keyboard.row(
                types.InlineKeyboardButton(
                    "🟢 Blokdan chiqarish",
                    callback_data=f"unblock:{target_id}"
                )
            )

        else:

            keyboard.row(
                types.InlineKeyboardButton(
                    "🚫 Bloklash",
                    callback_data=f"block:{target_id}"
                )
            )

        keyboard.row(
            types.InlineKeyboardButton(
                "🔄 Kanallarni tekshirish",
                callback_data=f"channels:{target_id}"
            )
        )

        keyboard.row(
            types.InlineKeyboardButton(
                "🔙 Foydalanuvchilar",
                callback_data="users"
            )
        )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # BLOCK
    # =====================================================

    elif call.data.startswith("block:"):

        if user_id != ADMIN_ID:
            return

        target_id = int(
            call.data.split(":", 1)[1]
        )

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE users
            SET blocked = 1
            WHERE user_id = ?
        """, (target_id,))

        db.commit()
        db.close()

        bot.send_message(
            call.message.chat.id,
            "🚫 Foydalanuvchi bloklandi."
        )


    # =====================================================
    # UNBLOCK
    # =====================================================

    elif call.data.startswith("unblock:"):

        if user_id != ADMIN_ID:
            return

        target_id = int(
            call.data.split(":", 1)[1]
        )

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE users
            SET blocked = 0
            WHERE user_id = ?
        """, (target_id,))

        db.commit()
        db.close()

        bot.send_message(
            call.message.chat.id,
            "🟢 Foydalanuvchi blokdan chiqarildi."
        )


    # =====================================================
    # CHANNEL CHECK
    # =====================================================

    elif call.data.startswith("channels:"):

        if user_id != ADMIN_ID:
            return

        target_id = int(
            call.data.split(":", 1)[1]
        )

        user = get_user(target_id)

        if not user:
            return

        text = f"""
👤 <b>{user[1]}</b>

🆔 ID: <code>{target_id}</code>

📢 <b>KANALLAR:</b>

"""

        for channel in CHANNELS:

            result = check_channel_member(
                target_id,
                channel["username"]
            )

            if result is True:

                text += (
                    f"{channel['name']} — "
                    f"✅ A'ZO\n"
                )

            elif result is False:

                text += (
                    f"{channel['name']} — "
                    f"❌ A'ZO EMAS\n"
                )

            else:

                text += (
                    f"{channel['name']} — "
                    f"⚠️ Tekshirib bo'lmadi\n"
                )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML"
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    elif call.data == "stats":

        if user_id != ADMIN_ID:
            return

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE blocked = 0"
        )
        active = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE blocked = 1"
        )
        blocked = cursor.fetchone()[0]

        today = str(date.today())

        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE substr(joined_date, 1, 10) = ?
        """, (today,))

        today_users = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(referrals), 0)
            FROM users
        """)

        referrals = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(xp), 0)
            FROM users
        """)

        total_xp = cursor.fetchone()[0]

        db.close()

        bot.send_message(
            call.message.chat.id,

            f"""
📊 <b>DARKCAMPER STATISTIKA</b>

👥 Jami foydalanuvchilar: {total}
🟢 Aktiv: {active}
🚫 Bloklangan: {blocked}

🆕 Bugun qo'shilgan: {today_users}

🔗 Jami referallar: {referrals}

⭐ Jami XP: {total_xp}

🤖 Bot holati: 🟢 Ishlayapti
""",

            parse_mode="HTML"
        )


    # =====================================================
    # BROADCAST
    # =====================================================

    elif call.data == "broadcast":

        if user_id != ADMIN_ID:
            return

        msg = bot.send_message(
            call.message.chat.id,
            """
📢 <b>BROADCAST</b>

Barcha foydalanuvchilarga yubormoqchi
bo'lgan xabaringizni yuboring.

Matn, rasm yoki video yuborishingiz mumkin.
""",
            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            broadcast_message
        )


    # =====================================================
    # SEARCH USER
    # =====================================================

    elif call.data == "search_user":

        if user_id != ADMIN_ID:
            return

        msg = bot.send_message(
            call.message.chat.id,
            """
🔎 <b>USER QIDIRISH</b>

Telegram ID yuboring:
""",
            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            search_user
        )


    # =====================================================
    # FEEDBACKS
    # =====================================================

    elif call.data == "feedbacks":

        if user_id != ADMIN_ID:
            return

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT user_id, text, date
            FROM feedback
            ORDER BY id DESC
            LIMIT 20
        """)

        feedbacks = cursor.fetchall()

        db.close()

        if not feedbacks:

            bot.send_message(
                call.message.chat.id,
                "💬 Hozircha feedback yo'q."
            )

            return

        text = "💬 <b>SO'NGGI FEEDBACKLAR</b>\n\n"

        for item in feedbacks:

            text += (
                f"🆔 <code>{item[0]}</code>\n"
                f"📝 {item[1]}\n"
                f"🕐 {item[2]}\n"
                f"━━━━━━━━━━━━\n"
            )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML"
        )


    # =====================================================
    # ADMIN HOME
    # =====================================================

    elif call.data == "admin_home":

        if user_id != ADMIN_ID:
            return

        bot.send_message(
            call.message.chat.id,
            "👑 <b>ADMIN PANEL</b>",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )


# =========================================================
# CHANNEL CHECK FUNCTION
# =========================================================

def check_channel_member(user_id, channel_username):

    try:

        member = bot.get_chat_member(
            channel_username,
            user_id
        )

        if member.status in [
            "creator",
            "administrator",
            "member"
        ]:
            return True

        return False

    except Exception as error:

        print(
            f"Channel error: "
            f"{channel_username} | {error}"
        )

        return None


# =========================================================
# FEEDBACK QABUL QILISH
# =========================================================

def receive_feedback(message):

    if is_blocked(message.from_user.id):
        return

    text = message.text

    if not text:
        bot.send_message(
            message.chat.id,
            "❌ Faqat matn yuboring."
        )
        return

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO feedback
        (user_id, text, date)
        VALUES (?, ?, ?)
    """, (
        message.from_user.id,
        text,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    db.commit()
    db.close()

    add_xp(
        message.from_user.id,
        5
    )

    bot.send_message(
        message.chat.id,

        """
✅ <b>Feedback qabul qilindi!</b>

Rahmat. Sizning fikringiz admin panelga yuborildi.

⭐ +5 XP
""",

        parse_mode="HTML"
    )

    try:

        bot.send_message(
            ADMIN_ID,

            f"""
💬 <b>YANGI FEEDBACK</b>

👤 {message.from_user.first_name}
🆔 <code>{message.from_user.id}</code>

📝 {text}
""",

            parse_mode="HTML"
        )

    except:
        pass


# =========================================================
# USER QIDIRISH
# =========================================================

def search_user(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        target_id = int(message.text)

    except:

        bot.send_message(
            message.chat.id,
            "❌ ID noto'g'ri."
        )

        return

    user = get_user(target_id)

    if not user:

        bot.send_message(
            message.chat.id,
            "❌ Bunday foydalanuvchi topilmadi."
        )

        return

    username = (
        "@" + user[2]
        if user[2]
        else "Username yo'q"
    )

    status = (
        "🚫 Bloklangan"
        if user[11]
        else "🟢 Aktiv"
    )

    bot.send_message(
        message.chat.id,

        f"""
👤 <b>USER TOPILDI</b>

👤 Ism: {user[1]}
🔗 Username: {username}
🆔 ID: <code>{user[0]}</code>

⭐ XP: {user[5]}
🏅 Level: {user[6]}
🔥 Streak: {user[7]}
👥 Referral: {user[9]}

📅 Ro'yxatdan o'tgan:
{user[3]}

📌 Holat:
{status}
""",

        parse_mode="HTML"
    )


# =========================================================
# BROADCAST
# =========================================================

def broadcast_message(message):

    if message.from_user.id != ADMIN_ID:
        return

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE blocked = 0
    """)

    users = cursor.fetchall()

    db.close()

    sent = 0
    failed = 0

    for row in users:

        target_id = row[0]

        try:

            if message.content_type == "text":

                bot.send_message(
                    target_id,
                    message.text
                )

            elif message.content_type == "photo":

                bot.send_photo(
                    target_id,
                    message.photo[-1].file_id,
                    caption=message.caption
                )

            elif message.content_type == "video":

                bot.send_video(
                    target_id,
                    message.video.file_id,
                    caption=message.caption
                )

            elif message.content_type == "document":

                bot.send_document(
                    target_id,
                    message.document.file_id,
                    caption=message.caption
                )

            else:

                failed += 1
                continue

            sent += 1

            time.sleep(0.05)

        except Exception as error:

            failed += 1
            print(
                f"Broadcast error: {target_id} | {error}"
            )

    bot.send_message(
        message.chat.id,

        f"""
📢 <b>BROADCAST YAKUNLANDI</b>

✅ Yuborildi: {sent}
❌ Xatolik: {failed}

👥 Jami: {len(users)}
""",

        parse_mode="HTML"
    )


# =========================================================
# UNKNOWN MESSAGE
# =========================================================

@bot.message_handler(
    func=lambda message: True,
    content_types=["text"]
)
def all_messages(message):

    if message.text.startswith("/"):
        return

    if is_blocked(message.from_user.id):
        return

    save_user(message.from_user)

    # Oddiy javob
    bot.send_message(
        message.chat.id,

        """
🤖 DARKCAMPER

Men sizning xabaringizni oldim.

Asosiy menyudan kerakli bo'limni tanlang 👇
""",

        reply_markup=main_menu()
    )


# =========================================================
# ISHGA TUSHIRISH
# =========================================================

print("================================")
print("🔥 DARKCAMPER BOT ISHLADI")
print("🗄️ SQLite Database: ON")
print("👑 Admin Panel: ON")
print("🎓 Academy: ON")
print("🏆 XP System: ON")
print("🔗 Referral: ON")
print("📊 Statistics: ON")
print("================================")

bot.infinity_polling(
    skip_pending=True
)
