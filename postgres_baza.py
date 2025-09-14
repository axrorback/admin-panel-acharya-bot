import psycopg2
from psycopg2 import sql, errors

DB_NAME = "bot_database"
DB_USER = "axrorback"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# 1) Avval postgres bazasiga ulanib, database yaratiladi
conn = psycopg2.connect(
    dbname="postgres",  # default baza
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
conn.autocommit = True
cursor = conn.cursor()

# Agar mavjud bo‘lmasa, CREATE DATABASE qilamiz
try:
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
    print(f"✅ Database '{DB_NAME}' yaratildi!")
except errors.DuplicateDatabase:
    print(f"ℹ️ Database '{DB_NAME}' allaqachon mavjud.")

cursor.close()
conn.close()

# 2) Endi yangi yaratilgan databasega ulanib, jadvallarni yaratamiz
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# USERS jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    full_name TEXT,
    username TEXT,
    language TEXT DEFAULT 'uz',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ADMINS jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# USER_MESSAGES jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT,
    message_text TEXT NOT NULL,
    admin_msg_id BIGINT,
    language TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# APPLICATIONS jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    application_number TEXT UNIQUE NOT NULL,
    telegram_id BIGINT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    faculty TEXT NOT NULL,
    status TEXT DEFAULT 'Yangi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# OTP jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS otps (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
)
""")

conn.commit()
cursor.close()
conn.close()
print("✅ PostgreSQL database va jadvallar tayyor!")
