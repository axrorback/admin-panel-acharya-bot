import sqlite3
from supabase import create_client

# Supabase ulanishi
SUPABASE_URL = "https://vlvwptbqqacqyyophsba.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZsdndwdGJxcWFjcXl5b3Boc2JhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMTU5OTYsImV4cCI6MjA2ODY5MTk5Nn0.gYmGKAxSyg27p0YE4_lepLtcj-myuaEj756kLpJ8O8U"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DB_NAME = "bot_database.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# user_messages dan barcha datani olish
response = supabase.table("user_messages").select("*").execute()
messages = response.data

for msg in messages:
    cursor.execute("""
        INSERT OR IGNORE INTO user_messages (user_id, username, message_text, admin_msg_id, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        msg["user_id"],
        msg.get("username"),
        msg.get("message_text"),
        msg.get("admin_msg_id"),
        msg.get("language"),
        msg.get("created_at")
    ))

conn.commit()
conn.close()
print(f"✅ {len(messages)} ta message ko‘chirildi!")
