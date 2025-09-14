import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "bot_database.db"

username = input("Yangi admin username: ")
password = input("Parol: ")
full_name = input("Full name: ")
telegram_id = input("Telegram ID: ")

# 🔑 Rol kiritish (default superadmin qilishingiz mumkin)
role = input("Rolni kiriting (superadmin/moderator/viewer): ").strip().lower()
if role not in ["superadmin", "moderator", "viewer"]:
    print("⚠️ Noto‘g‘ri rol kiritildi! Default sifatida 'viewer' berildi.")
    role = "viewer"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
INSERT INTO admins (telegram_id, full_name, username, password_hash, role)
VALUES (?, ?, ?, ?, ?)
""", (telegram_id, full_name, username, generate_password_hash(password), role))

conn.commit()
conn.close()

print(f"✅ Admin muvaffaqiyatli yaratildi! (Rol: {role})")
