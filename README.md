## Admin Panel + Telegram Bot (Acharya)

Bu loyiha Flask admin panel va Aiogram Telegram botdan iborat.

## 1) Talablar

- Python 3.10+ tavsiya qilinadi
- `pip` o‘rnatilgan bo‘lishi kerak

## 2) Loyihani tayyorlash

1. Loyihaga kiring:
   ```bash
   cd /tmp/workspace/axrorback/admin-panel-acharya-bot
   ```
2. Virtual environment yarating:
   ```bash
   python3 -m venv .venv
   ```
3. Virtual environment ni yoqing:
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
4. Kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

## 3) .env fayl sozlash

`.env_sample` asosida `.env` yarating:

```bash
cp .env_sample .env
```

`.env` ichida quyidagi qiymatlarni to‘ldiring:

- `TOKEN` = Telegram bot token
- `CHANNEL_ID` = kanal ID
- `ADMIN` = admin telegram ID(lar), bir nechta bo‘lsa vergul bilan
- `DB` = sqlite database nomi (masalan: `bot_database.db`)

Ixtiyoriy (Supabase’dan ko‘chirish skriptlari uchun):

- `URL` = Supabase URL
- `KEY` = Supabase key

## 4) Database yaratish

```bash
python init_db.py
```

## 5) Admin yaratish (ixtiyoriy, lekin tavsiya)

```bash
python create_admin.py
```

## 6) Botni ishga tushirish

```bash
python bot.py
```

## 7) Admin panelni ishga tushirish

Yangi terminal oching (virtual env aktiv holatda) va:

```bash
python app.py
```

Default holatda Flask app:

- `http://127.0.0.1:9002`

## 8) Supabase’dan ma’lumot ko‘chirish (ixtiyoriy)

- Foydalanuvchilar:
  ```bash
  python copy_user_from-supabase.py
  ```
- Xabarlar:
  ```bash
  python copy-mesg-from-supabase.py
  ```
