import sqlite3
from supabase import create_client

# Supabase ulanishi
SUPABASE_URL = "https://vlvwptbqqacqyyophsba.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZsdndwdGJxcWFjcXl5b3Boc2JhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMTU5OTYsImV4cCI6MjA2ODY5MTk5Nn0.gYmGKAxSyg27p0YE4_lepLtcj-myuaEj756kLpJ8O8U"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DB_NAME = "bot_database.db"

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
