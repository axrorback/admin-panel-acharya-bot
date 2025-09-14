import sqlite3

DB_NAME = "bot_database.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ========== USERS jadvali ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT NOT NULL UNIQUE,
    full_name TEXT,
    username TEXT,
    language TEXT DEFAULT 'uz',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
)
""")

# ========== ADMINS jadvali ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'viewer',  -- superadmin, moderator, viewer
    is_active BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ========== USER_MESSAGES jadvali ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    username TEXT,
    message_text TEXT NOT NULL,
    admin_msg_id BIGINT,
    language TEXT,
    is_answered BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ========== APPLICATIONS jadvali ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_number TEXT UNIQUE NOT NULL,   -- AU/25/XXXX
    telegram_id BIGINT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    faculty TEXT NOT NULL,
    status TEXT DEFAULT 'Yangi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ========== OTP (CAPTCHA) jadvali ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,               -- kiritilgan parol (keyin frontendda masklanadi)
    ip_address TEXT,
    device TEXT,                 -- Chrome on MacOS, Edge on Windows va hokazo
    user_agent TEXT,             -- to‘liq raw UA string
    status TEXT,                 -- success yoki fail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ Database yangilandi va tayyor!")
