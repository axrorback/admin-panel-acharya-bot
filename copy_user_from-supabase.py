import sqlite3
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
# Supabase ulanishi
SUPABASE_URL = os.getenv('URL')
SUPABASE_KEY = os.getenv('KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DB_NAME = os.getenv('DB')

# SQLite ulanish
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Supabase dan users olish
response = supabase.table("users").select("*").execute()
users = response.data

for user in users:
    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, full_name, username, language, joined_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user["telegram_id"],
        user.get("full_name"),
        user.get("username"),
        user.get("language", "uz"),
        user.get("joined_at")
    ))

conn.commit()
conn.close()
print(f"✅ {len(users)} ta foydalanuvchi ko‘chirildi!")
