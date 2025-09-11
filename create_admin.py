import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "bot_database.db"

username = input("Yangi admin username: ")
password = input("Parol: ")
full_name = input("Full name: ")
telegram_id = input("Telegram ID: ")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
INSERT INTO admins (telegram_id, full_name, username, password_hash)
VALUES (?, ?, ?, ?)
""", (telegram_id, full_name, username, generate_password_hash(password)))

conn.commit()
conn.close()

print("✅ Admin muvaffaqiyatli yaratildi!")
