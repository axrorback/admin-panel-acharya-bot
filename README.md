# Acharya Admin Panel & Telegram Bot

A management platform consisting of a Flask-based Admin Panel and an
Aiogram-powered Telegram Bot.

## Requirements

Before running the project, make sure the following software is
installed:

-   Python 3.10 or newer
-   pip (Python package manager)
-   Git (optional)

Verify Python:

``` bash
python --version
```

or

``` bash
python3 --version
```

------------------------------------------------------------------------

# Project Setup

## 1. Clone the Repository

``` bash
git clone <repository-url>
cd admin-panel-acharya-bot
```

Or:

``` bash
cd /path/to/admin-panel-acharya-bot
```

## 2. Create a Virtual Environment

### Linux / macOS

``` bash
python3 -m venv .venv
```

### Windows

``` powershell
python -m venv .venv
```

## 3. Activate the Virtual Environment

### Linux / macOS

``` bash
source .venv/bin/activate
```

### Windows (PowerShell)

``` powershell
.venv\Scripts\Activate.ps1
```

## 4. Install Dependencies

``` bash
pip install -r requirements.txt
```

Verify installation:

``` bash
pip list
```

------------------------------------------------------------------------

# Environment Configuration

## 5. Create the Environment File

### Linux / macOS

``` bash
cp .env_sample .env
```

### Windows

``` powershell
copy .env_sample .env
```

## 6. Configure Environment Variables

``` env
TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHANNEL_ID=-1001234567890
ADMIN=123456789
DB=bot_database.db
```

### Variables

  Variable     Description
  ------------ -------------------------------------------
  TOKEN        Telegram bot token from BotFather
  CHANNEL_ID   Telegram channel ID
  ADMIN        Admin Telegram ID(s), separated by commas
  DB           SQLite database filename

Example:

``` env
TOKEN=1234567890:AAExampleBotToken
CHANNEL_ID=-1009876543210
ADMIN=111111111,222222222
DB=bot_database.db
```

------------------------------------------------------------------------

# Database Initialization

## 7. Create Database Tables

``` bash
python init_db.py
```

------------------------------------------------------------------------

# Create an Administrator Account

## 8. Create Admin User

``` bash
python create_admin.py
```

------------------------------------------------------------------------

# Running the Telegram Bot

## 9. Start the Bot

``` bash
python bot.py
```

The bot should connect to Telegram and begin processing updates.

------------------------------------------------------------------------

# Running the Admin Panel

## 10. Start Flask Application

Open a new terminal, activate the virtual environment, and run:

``` bash
python app.py
```

Default address:

``` text
http://127.0.0.1:9002
```

Open the URL in your browser and log in with your administrator
credentials.

------------------------------------------------------------------------

# Project Structure

``` text
admin-panel-acharya-bot/
│
├── app.py
├── bot.py
├── init_db.py
├── create_admin.py
├── requirements.txt
├── .env
├── .env_sample
│
├── database/
├── handlers/
├── templates/
├── static/
└── utils/
```

------------------------------------------------------------------------

# Common Troubleshooting

### Virtual environment not activated

Activate it again:

``` bash
source .venv/bin/activate
```

### Missing packages

``` bash
pip install -r requirements.txt
```

### Database errors

``` bash
python init_db.py
```

### Bot does not start

Verify:

-   TOKEN is correct
-   Internet connection is available
-   Bot is not running elsewhere

------------------------------------------------------------------------

# Quick Start

``` bash
git clone https://github.com/axrorback/admin-panel-acharya-bot.git

cd admin-panel-acharya-bot

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp .env_sample .env

python init_db.py

python create_admin.py

python bot.py
```

In another terminal:

``` bash
source .venv/bin/activate

python app.py
```
