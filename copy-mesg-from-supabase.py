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
