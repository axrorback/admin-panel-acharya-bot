import logging
import asyncio
import os
import sqlite3
from collections import defaultdict
from email.policy import default
from pyexpat.errors import messages
from datetime import datetime

import aiogram
import supabase
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeDefault, \
    MenuButtonCommands, InputMediaPhoto, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from dotenv import load_dotenv
from collections import defaultdict
# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
from supabase import create_client , Client
from aiogram.types import Message
DB_NAME = "bot_database.db"
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
# .env fayldan tokenlarni olish
load_dotenv()
TOKEN = "8099179109:AAEHi2ZNiCW1xW2ESKsKFHeu2LfhH3r89us"
CHANNEL_ID = "-1003051981115"
ADMIN_ID =  [5789956459]

# Bot va dispatcher obyektlarini yaratamiz
bot = Bot(token=TOKEN)
dp = Dispatcher()

# FSM uchun holatlar
class Registration(StatesGroup):
    full_name = State()
    birth_date = State()
    region = State()
    district = State()
    phone = State()
class ContactForm(StatesGroup):
    waiting_for_message = State()

# Foydalanuvchi tillarini saqlash
user_language = {}

async def set_bot_menu():
    commands = [
        BotCommand(command="start", description="Botni yangilash"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

def main_menu(language):
    buttons = {
        "uz": [
            ("📌 Acharya haqida", "about"),
            ("📑 Hujjat topshirish", "apply"),
            ("📚 Fakultetlar", "faculties"),
            ("✒️ Habar Yozish", "contact"),
            ("📞 Qo‘ng‘iroq qiling", "call_centr"),
            ("👨‍💻 Dasturchi haqida", "developer"),
        ],
        "en":[
            ("📌 About Acharya", "about"),
            ("📑 Admission menu", "apply"),
            ("📚 Faculties", "faculties"),
            ("✒️ Write a Message", "contact"),
            ("📞 Call Center", "call_centr"),
            ("👨‍💻 About the Developer", "developer")
        ],
        "ru":[
            ("📌 О Ачарья ", "about"),
            ("📑 Подать документы", "apply"),
            ("📚 Факультеты", "faculties"),
            ("✒️ Написать сообщение", "contact"),
            ("📞 Колл-центр", "call_centr"),
            ("👨‍💻 О разработчике", "developer")

        ]
    }
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data)] for text, data in buttons.get(language, [])
        ]
    )
    return keyboard

@dp.message(Command("start"))
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    conn = get_db_connection()
    cursor = conn.cursor()

    # Foydalanuvchi mavjudligini tekshiramiz
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    existing = cursor.fetchone()

    if not existing:
        # Agar mavjud bo‘lmasa qo‘shamiz
        cursor.execute("""
            INSERT INTO users (telegram_id, full_name, username)
            VALUES (?, ?, ?)
        """, (telegram_id, full_name, username))
        conn.commit()

    conn.close()

    # Til tanlash klaviaturasi
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

    await message.answer(
        "tilni tanlang / выберите язык / select language",
        reply_markup=keyboard
    )
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: types.CallbackQuery):
    language = call.data.split("_")[1]
    user_language[call.from_user.id] = language
    habar = {
        "uz":"😊 Kerakli bo‘limni tanlang ⤵️",
        "en":"Select the desired section ⤵️",
        "ru":"😊 Выберите нужный раздел ⤵️"
    }
    await call.message.edit_text(habar[language], reply_markup=main_menu(language))

# @dp.callback_query(F.data == "apply")
# async def apply_registration(call: types.CallbackQuery, state: FSMContext):
#     await state.set_state(Registration.full_name)
#     await call.message.answer("Ro‘yxatdan o‘tish uchun ismingizni kiriting:")
@dp.callback_query(F.data == "back_faculties")
async def back_to_faculties(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    faculty_list = {
        "uz": [
            ("Kompyuter injiniringi (B.Tech)", "faculty_computer"),
            ("Ma'lumotlar fani (B.Tech)", "faculty_data"),
            ("Sun'iy intellekt (B.Tech)", "faculty_ai"),
            ("Bulutli hisoblash va xavfsizlik (B.Tech)", "faculty_cyber"),
            ("Bulutli hisoblash (BCA)", "faculty_cyber1"),
            ("Axborot texnologiyalari (BCA)", "faculty_tech"),
            ("Ma'lumotlar tahlili (BCA)", "faculty_analytics"),
            ("Fullstack Developer (BCA)", "faculty_fullstack"),
            ("UI & UX Dizayn (BCA)", "faculty_design"),
            ("Biznes tahlili (BCA)", "faculty_business"),
            ("Fintech (BCA)", "faculty_fintech"),
            ("Raqamli marketing (BCA)", "faculty_marketing"),
        ],
        "en": [
            ("Computer Engineering (B.Tech)", "faculty_computer_en"),
            ("Data Science (B.Tech)", "faculty_data_en"),
            ("Artificial Intelligence (B.Tech)", "faculty_ai_en"),
            ("Cloud Computing & Security (B.Tech)", "faculty_cyber_en"),
            ("Cloud Computing (BCA)", "faculty_cyber1_en"),
            ("Information Technology (BCA)", "faculty_tech_en"),
            ("Data Analytics (BCA)", "faculty_analytics_en"),
            ("Fullstack Development (BCA)", "faculty_fullstack_en"),
            ("UI & UX Design (BCA)", "faculty_design_en"),
            ("Business Analysis (BCA)", "faculty_business_en"),
            ("Fintech (BCA)", "faculty_fintech_en"),
            ("Digital Marketing (BCA)", "faculty_marketing_en"),
        ],
        "ru": [
            ("Компьютерная инженерия (B.Tech)", "faculty_computer_ru"),
            ("Наука о данных (B.Tech)", "faculty_data_ru"),
            ("Искусственный интеллект (B.Tech)", "faculty_ai_ru"),
            ("Облачные вычисления и безопасность (B.Tech)", "faculty_cyber_ru"),
            ("Облачные вычисления (BCA)", "faculty_cyber1_ru"),
            ("Информационные технологии (BCA)", "faculty_tech_ru"),
            ("Аналитика данных (BCA)", "faculty_analytics_ru"),
            ("Fullstack разработка (BCA)", "faculty_fullstack_ru"),
            ("UI & UX дизайн (BCA)", "faculty_design_ru"),
            ("Бизнес-анализ (BCA)", "faculty_business_ru"),
            ("Финансовые технологии (BCA)", "faculty_fintech_ru"),
            ("Цифровой маркетинг (BCA)", "faculty_marketing_ru"),
        ]
    }

    # Fakultet tugmalari
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=cb)]
        for name, cb in faculty_list[lang]
    ]

    # Orqaga tugmasi (3 tilda)
    back_button = {
        "uz": "⬅️ Ortga",
        "en": "⬅️ Back",
        "ru": "⬅️ Назад"
    }
    buttons.append([InlineKeyboardButton(text=back_button[lang], callback_data="back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    habar = {
        "uz": "📚 Fakultetlar ro'yxati",
        "en": "📚 List of Faculties",
        "ru": "📚 Список факультетов"
    }

    # Eski (rasm yoki matn) xabarni o‘chiramiz
    try:
        await call.message.delete()
    except:
        pass

    # Yangi matnli xabar yuboramiz
    await call.message.answer(habar[lang], reply_markup=keyboard)

    await call.answer()



@dp.callback_query(F.data == "faculties")
async def faculties_menu(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    faculty_data = {
        "uz": [
            ("Kompyuter injiniringi (B.Tech)", "faculty_computer"),
            ("Malumotlar Fani (B.Tech)", "faculty_data"),
            ("Sun'iy Intelekt (B.Tech)", "faculty_ai"),
            (" Bulutli xisoblash va xafsizlik (B.Tech)", "faculty_cyber"),
            (" Bulutli xisoblash (BCA)", "faculty_cyber1"),
            (" Axborot Texnologiyalari (BCA)", "faculty_tech"),
            (" Malumotlar Tahlili (BCA)", "faculty_analytics"),
            (" Fullstack Developer (BCA)", "faculty_fullstack"),
            (" UI & UX Dizayn (BCA)", "faculty_design"),
            (" Biznes Tahlili (BCA)", "faculty_business"),
            (" Fintech (BCA)", "faculty_fintech"),
            (" Raqamli Marketing (BCA)", "faculty_marketing"),

        ],
        "en":[
        ("Computer Engineering (B.Tech)", "faculty_computer_en"),
        ("Data Science (B.Tech)", "faculty_data_en"),
        ("Artificial Intelligence (B.Tech)", "faculty_ai_en"),
        ("Cloud Computing & Security (B.Tech)", "faculty_cyber_en"),
        ("Cloud Computing (BCA)", "faculty_cyber1_en"),
        ("Information Technology (BCA)", "faculty_tech_en"),
        ("Data Analytics (BCA)", "faculty_analytics_en"),
        ("Fullstack Development (BCA)", "faculty_fullstack_en"),
        ("UI & UX Design (BCA)", "faculty_design_en"),
        ("Business Analysis (BCA)", "faculty_business_en"),
        ("Fintech (BCA)", "faculty_fintech_en"),
        ("Digital Marketing (BCA)", "faculty_marketing_en"),
    ],
        "ru":[
        ("Компьютерная инженерия (B.Tech)", "faculty_computer_ru"),
        ("Наука о данных (B.Tech)", "faculty_data_ru"),
        ("Искусственный интеллект (B.Tech)", "faculty_ai_ru"),
        ("Облачные вычисления и безопасность (B.Tech)", "faculty_cyber_ru"),
        ("Облачные вычисления (BCA)", "faculty_cyber1_ru"),
        ("Информационные технологии (BCA)", "faculty_tech_ru"),
        ("Аналитика данных (BCA)", "faculty_analytics_ru"),
        ("Fullstack разработка (BCA)", "faculty_fullstack_ru"),
        ("UI & UX дизайн (BCA)", "faculty_design_ru"),
        ("Бизнес-анализ (BCA)", "faculty_business_ru"),
        ("Финансовые технологии (BCA)", "faculty_fintech_ru"),
        ("Цифровой маркетинг (BCA)", "faculty_marketing_ru"),

    ]
    }

    buttons = [
        [InlineKeyboardButton(text=name, callback_data=callback)]
        for name, callback in faculty_data[lang]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    habar = {
        "uz":"Fakultetlar Ro'yhati",
        "en":" List of Faculties",
        "ru":"Список факультетов"
    }
    await call.message.edit_text(habar[lang], reply_markup=keyboard)




@dp.callback_query(F.data.startswith("faculty_"))
async def faculty_info(call: types.CallbackQuery):
    faculty_data = {
        "faculty_computer": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Kompyuter injiniringi (B.Tech)\n\nDastur tafsilotlari Kompyuter fanlari va muhandislik bo'yicha malakali bitiruvchilarga bolgan global talab sohalar boylab uning tushunchalarini qollashning kengayishi tufayli osib bormoqda.\nDastur talabalarga kompyuter fanidagi asosiy kompetensiyalari bilan innovatsion ish olib borayotganda, real muammolar ustida ishlash bilan bog'liq muammolarni o'z ichiga olgan martabalarni olishga imkon beradi."
        },
        "faculty_data": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Ma'lumotlar Ilmi (B.Tech)\n\nBugungi dunyo ma'lumotlarga asoslangan bo'lib, qarorlar va yechimlar aniq bo'lishi kerak. Ma'lumotlar fani biznesning faoliyat ko'rsatishini o'zgartirmoqda, ayniqsa texnologiya sektori rivojlanayotgan iqtisodiyotlarda.\nMa'lumotlar ilm-fani dasturi matematika, statistika va kompyuter fanlari bo'yicha asosiy kurslar orqali amaliy yechimlarni ishlab chiqish uchun ma'lumotlar va kerakli hisoblash ko'nikmalarini o'rganishda ilm-fanni tushunishga o'rgatilgan ishchi kuchini ishlab chiqarishni maqsad qilgan."
        },
        "faculty_ai": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Sun'iy Intelekt (B.Tech)\n\nSun'iy intellekt va mashinalarni o'rganishga bo'lgan talab ortib bormoqda, Jahon Iqtisodiy Forumining Ishlarning kelajagi 2023 hisoboti shuni ko'rsatadiki, 2027 yilga kelib ushbu sohadagi mutaxassislarga bo'lgan talab 40 foizga ko'payadi.\nAcharya's AI va Machine Learning dasturi kompyuter fanlari, ma'lumotlar fanlari, matematika va inson fanlari bilan kesishgan fanlararo sohadir. Talabalar zamonaviy laboratoriyalar va ilg'or texnologiyalar bilan ta'minlanib, amaliy tajriba va nazariy bilimlarni amaliyotga tatbiq etishni ta'minlaydilar."
        },
        "faculty_cyber":{
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Bulutli Hisoblash va Xavfsizlik (B.Tech)\n\nDastur onlayn tahdidlardan himoya qilish uchun ma'lumotlarni va bulutli hisoblash muhitini himoya qilish uchun ishlatiladigan texnologiyalar va dasturlarga e'tibor qaratadi. Bu bulutda joylashtirilgan ma'lumotlar va dasturlarni himoya qilish uchun kuchli xavfsizlik choralarini ishlab chiqish va amalga oshirishni o'z ichiga oladi.\nBulut xavfsizligi bo'yicha malakali mutaxassislarga bo'lgan talab ortib bormoqda, Cybersecurity Ventures tadqiqotlari shuni ko'rsatadiki, kiber jinoyatchilik 2024 yilda global miqyosda 9,5 trillion dollarga tushadi, bu yilga nisbatan 15 foizga o'sadi va 2025 yilda 10,5 trillion dollarga yetadi. Bu shuni anglatadiki, kiberxavfsizlik bo'yicha mutaxassislarga onlayn maydondagi kompaniyalar uchun xavfsizlikni ta'minlash uchun zudlik bilan ehtiyoj bor."
        },
        "faculty_cyber1": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Bulutli hisoblash (BCA)\n\nMa'lumotlarni saqlash, serverlar, ma'lumotlar bazalari va boshqalar kabi xostlangan xizmatlardan Internet orqali foydalanish bulutli hisoblash deb nomlanadi. Bulutli hisoblash bo'yicha diplom talabalarga tizim boshqaruvchisi, bulutli maslahatchi, bulutli me'mor, xavfsizlik muhandisi va boshqalar sifatida ishlash imkoniyatini beradi."
        },
        "faculty_tech": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Axborot Texnologiyalari (BCA)\n\nAxborot texnologiyalari bo'yicha BCA bilan kompyuter dasturlash tillari dunyosiga kiring. Ushbu to'rt yillik kurs talabalarni dasturiy ta'minot ishlab chiqish, veb-ishlab chiqish, tizimlarni boshqarish bo'yicha kasbga tayyorlaydi. va IT sektoridagi boshqa faol rollar."
        },
        "faculty_analytics": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Ma'lumotlar Tahlili (BCA)\n\nDastur asosiy tushunchalar, texnologiyalar va ularning ma'lumotlar ilm-fani va biznes analitikasi, mashina o'rganishi, vizualizatsiya texnikasi va bashoratli modellashtirish bo'yicha chuqur bilimlarni o'rgatishni maqsad qilgan."
        },
        "faculty_fullstack": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Full Stack Dasturlash(BCA)\n\nIlovalarning frontend va backendlarini ishlab chiqish jarayoni to'liq stackni ishlab chiqish deb ataladi. To'liq to'plamni ishlab chiqish bo'yicha diplom talabalarga HTML va CSSni o'zlashtirishga yordam beradi, shuningdek, brauzer, server va ma'lumotlar bazasini dasturlashni o'rganadi."
        },
        "faculty_design": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " UI va UX dizayni (BCA)\n\nUI & UX dizayni boʻyicha diplom talabalarga vizual jihatdan jozibali va foydalanuvchilarga qulay interfeyslarni ishlab chiqish uchun zarur boʻlgan koʻnikmalarni beradi."
        },
        "faculty_business": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": "Biznes Tahlili (BBA-IT)\n\nUshbu to'rt yillik dastur ma'lumotlarni tahlil qilish va biznes-axborotning kombinatsiyasi bo'lib, talabalarga turli sohalardagi martaba uchun zarur bo'lgan bilim va amaliy ko'nikmalarni beradi. BBA biznes Analitika bitiruvchilari Hindistonda va chet ellarda keng imkoniyatlarga ega. Ushbu soha global biznes landshaftini butunlay o'zgartirdi, aksariyat korxonalar biznes tahlillarini o'z ichiga oladi kundalik faoliyatida. Natijada, butun dunyo bo'ylab BBA Business Analytics bitiruvchilariga ehtiyoj ortib bormoqda. Bir nechta milliy, ko'p millatli va elektron tijorat korxonalari ushbu mutaxassislarni yollamoqda. bitiruvchilarga raqobatbardosh ish haqi va boshqa imtiyozlar taklif qilmoqda."
        },
        "faculty_fintech": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " FinTech (BBA-IT)\n\nBBA In FinTech - bu innovatsion texnologiyalar tomonidan boshqariladigan sanoat talablarini qondirish uchun birlashtirilgan moliya va texnologiya fanlarini qamrab oladigan kursdir:\nBlokcheyn\nShun'iy intellekt\nBulutli hisoblash\nNimalar Interneti\nMobil hisoblash"
        },
        "faculty_marketing": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Raqamli Marketing (BBA-IT)\n\nRaqamli marketing - bu raqamli texnologiyalardan foydalangan holda turli xil mahsulotlar va xizmatlarni sotishni o'rganadigan kurs. Talabalar SEO (Search Engine Optimization), SEM (Search Engine Marketing), kontent marketingi, pulli media kabi turli sohalarda ko'plab ish imkoniyatlarini olishlari mumkin.\nBitiruvchilar o'z kasbiy faoliyatini raqamli marketing, elektron marketing, brendlash, korporativ sohadagi tadqiqotlar va maslahatlar sohasida ham boshlashlari mumkin."
        },
        "faculty_computer_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Computer Science And Engineering (B.Tech)\n\nThe global demand for qualified Computer Science and Engineering graduates are on the rise due to the expanding application of its concepts across sectors.\nThe program enables the students to undertake careers involving challenges of working on real-world problems, while innovating with their core competency in computer science."
        },
        "faculty_data_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Data Science (B.Tech)\n\nToday's world is a data-driven one where decisions and solutions need to be precise. Data science is transforming how businesses operate, especially in economies where the technology sector is booming.\nThe program in Data Science aims to produce manpower trained to understand the science in learning from data and the needed computing skills to develop practical solutions through foundational courses in mathematics, statistics and computer science."
        },
        "faculty_ai_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Artificial Intelligence and Machine Learning(B.Tech)\n\nThe demand for Artificial Intelligence and Machine Learning is on the rise, with the World Economic Forum's Future of Jobs 2023 report estimating that by 2027, the demand for specialists in the field will increase by 40%.\nAcharya’s AI and Machine Learning program is an interdisciplinary field that intersects with computer science, data science, mathematics and human science. Students benefit from state-of-the-art labs and cutting-edge technology, ensuring hands-on experience and practical application of theoretical knowledge."
        },
        "faculty_cyber_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Cloud Computing and Security (B.Tech)\n\nThe program focuses on the technologies and applications used to protect data and the cloud computing environment to protect against online threats. It involves designing and implementing strong security measures to protect data and applications hosted in the cloud.\nThe demand for qualified cloud security professionals are on the rise, with a Cybersecurity Ventures research noting that, cybercrime will cost $9.5 trillion globally in 2024, growing year over year by 15 percent, to a projected $10.5 trillion in 2025. This means, there’s an urgent need for cybersecurity professionals to maintain security for companies in the online space."
        },
        "faculty_cyber1_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": "Cloud Computing (BCA)\n\nThe use of hosted services, such as data storage, servers, databases, and more over the internet is called cloud computing. A degree in cloud computing will open up avenues for students to work as system administrator, cloud consultant, cloud architect, security engineer and more."
        },
        "faculty_tech_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Information Technology (BCA)\n\nDelve into the world of computer programming languages with BCA in Information Technology. This four-year-course prepares students for careers in software development, web development, systems management and other vibrant roles in the IT sector."
        },
        "faculty_analytics_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Data Analytics (BCA)\n\nThe program aims to impart in-depth knowledge on the key concepts, technologies, and its applications in data science & business analytics, machine learning, visualization techniques and predictive modeling."
        },
        "faculty_fullstack_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Full Stack Development (BCA)\n\nThe process of developing both the frontend and backend of applications is called full stack development. A degree in full stack development will help students master HTML and CSS and also learn to program a browser, program a server, and a database."
        },
        "faculty_design_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": "UI & UX Design (BCA)\n\nA degree in UI & UX Design will equip students with the necessary skills to develop visually appealing and user-friendly interfaces."
        },
        "faculty_business_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Business Analytics (BBA-IT)\n\nThis four-year-program is a combination of data analytics and business intelligence and equips students with the knowledge and practical skills necessary for careers in diverse sectors. BBA Business Analytics graduates have a wide range of opportunities in India and abroad. This field has completely revolutionized the global business landscape, with most businesses incorporating business analytics into their everyday operations. As a result, there is a growing need for BBA Business Analytics graduates around the world. Several national, multi-national, and e-commerce businesses are hiring these graduates, and they are offering them competitive salaries and other advantages."
        },
        "faculty_fintech_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " FinTech (BBA-IT)\n\nBBA In FinTech is a course that covers subjects of Finance and Technology that are blended to meet the industry requirement driven by innovative technologies such as:\nBlockchain\nArtificial Intelligence\nCloud Computing\nThe Internet of Things\nMobile Computing"
        },
        "faculty_marketing_en": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Digital Marketing (BBA-IT)\n\nDigital marketing is a course that is a study of marketing of different products and services using digital technologies. Students are able to get a number of job opportunities in various fields such as SEO (Search Engine Optimization) , SEM (Search Engine Marketing), Content Marketing, Paid Media.v\nGraduates can also start their professional career in fields of digital marketing, e-marketing, branding, research and consultancy in corporate."
        },
        "faculty_computer_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": "Компьютерные науки и инженерия(B.Tech)\n\nМировой спрос на выпускников по специальности  стремительно растет благодаря расширению применения её концепций в различных отраслях.."
        },
        "faculty_data_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Наука о данных (B.Tech)\n\nВступите в мир науки о данных в эпоху цифровых технологий. Современный мир движим данными, где решения должны быть точными. Наука о данных преобразует работу бизнеса."
        },
        "faculty_ai_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Искусственный интеллект (B.Tech)\n\nСпрос на специалистов в области искусственного интеллекта и машинного обучения стремительно растет. Согласно отчету Всемирного экономического форума «Будущее рабочих мест 2023»"
        },
        "faculty_cyber_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Облачные вычисления и безопасность (B.Tech)\n\nНачните востребованную карьеру в области облачной архитектуры с этой новой программы. Программа направлена на изучение технологий и приложений, используемых для защиты данных и облачной среды от онлайн-угроз"
        },
        "faculty_cyber1_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " ОБЛАЧНАЯ ОБРАБОТКА ДАННЫХ (B.Tech)\n\nОблачные вычисления включают использование таких услуг, как хранение данных, серверы, базы данных и другие ресурсы через интернет. Степень в области облачных вычислений откроет студентам возможность работать."
        },
        "faculty_tech_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Информационные технологии (BCA)\n\nБудьте в курсе требований технологического мира с программой BCA в области информационных технологий. Изучите мир языков компьютерного программирования"
        },
        "faculty_analytics_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Аналитика данных (BCA)\n\nПодготовьтесь к прибыльной карьере с учебным планом BCA Аналитика данных. Программа направлена на передачу глубоких знаний о ключевых концепциях, технологиях"
        },
        "faculty_fullstack_ru": {
            "image": "https://www .acharya.uz/images/applynow.jpg",
            "text": " РАЗРАБОТКА ПОЛНОСТЕКОВЫХ ПРИЛОЖЕНИЙ (BCA)\n\nИзучите захватывающую карьеру разработчика с программой BCA по разработке полного стека. Разработка полного стека включает создание как фронтенда, так и бэкенда приложений."
        },
        "faculty_design_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Ui и ux дизайн (BCA)\n\nСоздавайте потрясающие веб-сайты, приложения и другие пользовательские интерфейсы через эту программу. Степень в области UI & UX Design обеспечит студентов необходимыми навыками для разработки визуально привлекательных и удобных интерфейсов."
        },
        "faculty_business_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": "  Бизнес - аналитика (BBA-IT)\n\nНаучитесь предоставлять важнейшие аналитические решения для бизнеса. Эта четырехлетняя программа сочетает в себе аналитику данных и бизнес-аналитику, обеспечивая студентов знаниями и практическими навыками, необходимыми для карьеры в различных секторах"
        },
        "faculty_fintech_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Финтех (BCA)\n\nСвяжитесь с растущей и требовательной областью финансовых технологий с этим BBA. BBA в области FinTech — это курс, охватывающий темы финансов и технологий, которые объединяются для удовлетворения требований индустрии, управляемой инновационными технологиями"
        },
        "faculty_marketing_ru": {
            "image": "https://www.acharya.uz/images/applynow.jpg",
            "text": " Цифровой маркетинг (BBA-IT)\n\nИспользуйте цифровые технологии для управления и продвижения брендов, продуктов и услуг. Цифровой маркетинг — это курс, изучающий маркетинг различных продуктов и услуг с использованием цифровых технологий. Студенты получают множество возможностей для трудоустройства в различных областях, таких как SEO (поисковая оптимизация."
        },


    }

    faculty = faculty_data.get(call.data)
    if faculty:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_faculties")]]
        )
        # Yangi photo jo‘natish
        await call.message.answer_photo(
            photo=faculty["image"],
            caption=faculty["text"],
            reply_markup=keyboard
        )
        # Avvalgi xabarni o'chirish
        try:
            await call.message.delete()
        except aiogram.exceptions.TelegramBadRequest:
            pass


@dp.callback_query(F.data == "about")
async def handle_about(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    text = {
        "uz": (
            "🎓 *Acharya Universiteti haqida*\n\n"
            "✨ _Acharya Universitetiga xush kelibsiz!_\n\n"
            "🏫 Biz — Muhandislik, Axborot Texnologiyalari va Tibbiyot sohalarida "
            "jahon darajasidagi ta’lim berishga bag‘ishlangan *dinamik va innovatsion institut*miz.\n\n"
            "📚 Universitet quyidagilarni taklif etadi:\n"
            "• 🎓 *Bakalavriat va magistratura dasturlari*\n"
            "• 🔬 *Tadqiqot imkoniyatlari*\n"
            "• 🌍 *Zamonaviy o‘quv dasturlari*\n\n"
            "🎯 Maqsadimiz — talabalarni muvaffaqiyatli faoliyat va ilmiy izlanishlarga tayyorlash, "
            "hamda har bir yo‘nalishda mukammallikka erishishdir."
        ),
        "en": (
            "🎓 *About Acharya University*\n\n"
            "✨ _Welcome to Acharya University of Uzbekistan!_\n\n"
            "🏫 We are a *dynamic and innovative institution* dedicated to world-class education "
            "in *Engineering, Information Technology, and Medical Sciences*.\n\n"
            "📚 We offer:\n"
            "• 🎓 *Undergraduate & Graduate Programs*\n"
            "• 🔬 *Research Opportunities*\n"
            "• 🌍 *Cutting-edge Curriculum*\n\n"
            "🎯 Our mission is to prepare students for successful careers while fostering knowledge "
            "and innovation through a vibrant academic community."
        ),
        "ru": (
            "🎓 *Об Университете Ачарья*\n\n"
            "✨ _Добро пожаловать в Университет Ачарья в Узбекистане!_\n\n"
            "🏫 Мы — *динамичный и инновационный институт*, предоставляющий образование мирового уровня "
            "в области *инженерии, информационных технологий и медицины*.\n\n"
            "📚 Университет предлагает:\n"
            "• 🎓 *Бакалавриат и магистратуру*\n"
            "• 🔬 *Возможности для исследований*\n"
            "• 🌍 *Современные учебные программы*\n\n"
            "🎯 Наша цель — подготовить студентов к успешной карьере и научным достижениям, "
            "обеспечивая совершенство во всех направлениях."
        )
    }

    # Tugmalar
    site_button_text = {
        "uz": "🌐 Rasmiy sayt",
        "en": "🌐 Official Website",
        "ru": "🌐 Официальный сайт"
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=site_button_text[lang], url="https://www.acharya.uz")],
            [InlineKeyboardButton(text={"uz": "🔙 Orqaga", "en": "🔙 Back", "ru": "🔙 Назад"}[lang], callback_data="back")]
        ]
    )

    photo_url = "https://www.acharya.uz/en/images/news/inter-school/1a.jpg"

    await call.message.answer_photo(
        photo=photo_url,
        caption=text[lang],
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await call.message.delete()
@dp.callback_query(F.data == "apply")
async def handle_apply(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    # 3 tilda matn
    caption = {
        "uz": (
            "📑 **Hujjat topshirish**\n\n"
            "Acharya Universiteti 100 ta grantni munosib va bilimli talabalar uchun taklif etadi. "
            "Grantlar to‘liq va qisman shakllarda taqdim etiladi.\n\n"
            "🔹 Arizani topshirish usullari:\n"
            "1️⃣ **Ariza yuborish (Flask)** — shu bot bilan bog‘langan tizim orqali.\n"
            "2️⃣ **Sayt orqali hujjat topshirish** — universitetning rasmiy sahifasida.\n\n"
            "📊 **Ariza holatini tekshirish**:\n"
            "Agar siz avval ariza yuborgan bo‘lsangiz, uni holatini bilish uchun "
            "«📊 Ariza holatini ko‘rish» tugmasini bosing."
        ),
        "en": (
            "📑 **Application Submission**\n\n"
            "Acharya University offers **100 scholarships** for talented and deserving students. "
            "Scholarships are available in both **full and partial** forms.\n\n"
            "🔹 Submission methods:\n"
            "1️⃣ **Submit Application (Flask)** — via the system connected to this bot.\n"
            "2️⃣ **Submit via Website** — through the official university page.\n\n"
            "📊 **Check Application Status**:\n"
            "If you have already submitted an application, you can check its status by pressing "
            "the «📊 Check Application Status» button."
        ),
        "ru": (
            "📑 **Подача документов**\n\n"
            "Университет Ачарья предоставляет **100 грантов** для талантливых и достойных студентов. "
            "Гранты предоставляются полностью или частично.\n\n"
            "🔹 Способы подачи:\n"
            "1️⃣ **Отправить заявку (Flask)** — через систему, связанную с этим ботом.\n"
            "2️⃣ **Через сайт** — на официальной странице университета.\n\n"
            "📊 **Проверка статуса заявки**:\n"
            "Если вы уже отправили заявку, вы можете проверить её статус, "
            "нажав кнопку «📊 Проверить статус заявки»."
        )
    }

    # Tugmalar
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text={"uz": "📝 Ariza yuborish (Flask)", "en": "📝 Submit Application (Flask)",
                      "ru": "📝 Отправить заявку (Flask)"}[lang],
                url=f"https://127.0.0.1:5000/apply?user_id={call.from_user.id}"
            )],
            [InlineKeyboardButton(
                text={"uz": "🌐 Sayt orqali hujjat topshirish", "en": "🌐 Submit via Website", "ru": "🌐 Подать через сайт"}[lang],
                url="https://www.acharya.uz/uzb_reg/"
            )],
            [InlineKeyboardButton(
                text={"uz": "📊 Ariza holatini ko‘rish", "en": "📊 Check Application Status", "ru": "📊 Проверить статус заявки"}[lang],
                callback_data="check_status"
            )],
            [InlineKeyboardButton(
                text={"uz": "🔙 Orqaga", "en": "🔙 Back", "ru": "🔙 Назад"}[lang],
                callback_data="back"
            )]
        ]
    )

    # Rasm URL
    photo_url = "https://media.istockphoto.com/id/675073328/vector/admission-concept-on-keyboard-button-3d-rendering.jpg?s=612x612&w=0&k=20&c=rsDToN9NseYiS5WEw48w6J_Ll4eWafgbeBwgml5Q254="

    await call.message.answer_photo(photo=photo_url, caption=caption[lang], reply_markup=keyboard, parse_mode="Markdown")
    await call.message.delete()


@dp.callback_query(F.data == "contact")
async def handle_contact(call: types.CallbackQuery, state: FSMContext):
    lang = user_language.get(call.from_user.id, "uz")

    # Matnlar
    caption = {
        "uz": "✉️ Bizga habar qoldiring: Savollaringiz bo‘yicha quyidagi usullardan birini tanlang.",
        "en": "✉️ Write to us: Choose one of the options below to contact us.",
        "ru": "✉️ Напишите нам: Выберите один из способов связи ниже."
    }

    button_telegram = {
        "uz": "📨 Telegram orqali",
        "en": "📨 Via Telegram",
        "ru": "📨 Через Telegram"
    }

    button_bot = {
        "uz": "🤖 Bot orqali yozish",
        "en": "🤖 Write via Bot",
        "ru": "🤖 Написать через бота"
    }

    back = {
        "uz": "🔙 Orqaga",
        "en": "🔙 Back",
        "ru": "🔙 Назад"
    }

    photo_url = "https://contspace.ru/upload/iblock/c87/sv3abc5r9fxd0kh4evffg10f34tzjjzb/%D0%BA%D1%8C%D0%BD%D1%82%201.jpeg"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_telegram[lang], url="https://t.me/Acharya_support")],
        [InlineKeyboardButton(text=button_bot[lang], callback_data="contact_via_bot")],
        [InlineKeyboardButton(text=back[lang], callback_data="back")]
    ])

    await call.message.answer_photo(photo=photo_url, caption=caption[lang], reply_markup=keyboard)
    await call.message.delete()

@dp.callback_query(F.data == "contact_via_bot")
async def contact_via_bot(call: types.CallbackQuery, state: FSMContext):
    lang = user_language.get(call.from_user.id, "uz")
    prompt = {
        "uz": (
            "✍️ *Habar yuborish*\n\n"
            "Siz bizga o‘z fikringizni yoki savolingizni yozishingiz mumkin. "
            "Biz xabaringizni tez orada adminlarga yetkazamiz. 💬\n\n"
            "Iltimos, xabaringizni kiriting:"
        ),
        "en": (
            "✍️ *Send a Message*\n\n"
            "You can write your feedback or question here. "
            "We will forward your message to our admins as soon as possible. 💬\n\n"
            "Please type your message:"
        ),
        "ru": (
            "✍️ *Отправить сообщение*\n\n"
            "Вы можете написать своё мнение или вопрос здесь. "
            "Мы передадим ваше сообщение администраторам в ближайшее время. 💬\n\n"
            "Пожалуйста, введите сообщение:"
        )
    }
    await call.message.answer(prompt[lang], parse_mode="Markdown")
    await state.set_state(ContactForm.waiting_for_message)




@dp.callback_query(F.data == "back")
async def go_back(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    # Har bir til uchun matn
    back_text = {
        "uz": "😊 Kerakli bo‘limni tanlang ⤵️",
        "en": "😊 Please select the required section ⤵️",
        "ru": "😊 Пожалуйста, выберите нужный раздел ⤵️"
    }

    try:
        # Eski xabarni o‘chiramiz
        await call.message.delete()
    except Exception:
        pass  # Agar xato bo‘lsa, e’tiborsiz qoldiramiz

    # Yangi menyuni yuboramiz
    await call.message.answer(
        back_text[lang],
        reply_markup=main_menu(lang)
    )

    await call.answer()

@dp.message(ContactForm.waiting_for_message)
async def forward_user_message(message: types.Message, state: FSMContext):
    # Foydalanuvchi tilini olish
    lang = user_language.get(message.from_user.id, "uz")
    user = message.from_user
    user_id = user.id
    username = user.username
    full_name = user.full_name
    msg_text = message.text

    # Display name
    display_name = f"@{username}" if username else full_name

    # Adminlarga yuborish
    for admin_id in ADMIN_ID:
        sent = await message.bot.send_message(
            admin_id,
            f"📩 Yangi xabar:\n"
            f"👤 {display_name}\n"
            f"🆔 ID: {user_id}\n"
            f"🕒 {message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"💬 {msg_text}"
        )

        # SQLite bazaga yozish
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_messages (user_id, username, message_text, admin_msg_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            username or full_name,
            msg_text,
            sent.message_id,
            message.date.isoformat()
        ))
        conn.commit()
        conn.close()

    # Kanalga yuborish
    try:
        await message.bot.send_message(
            chat_id=CHANNEL_ID,
            text=(
                f"📩 Yangi xabar:\n"
                f"👤 {display_name}\n"
                f"🆔 ID: {user_id}\n"
                f"🕒 {message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"💬 {msg_text}"
            )
        )
    except Exception as e:
        print(f"❌ Kanalga yuborilmadi: {e}")

    # Foydalanuvchiga javob
    success = {
        "uz": "✅ Habar yuborildi. Tez orada javob olasiz.",
        "en": "✅ Your message has been sent. You will receive a reply soon.",
        "ru": "✅ Сообщение отправлено. Вы скоро получите ответ."
    }

    back = {
        "uz": "🔙 Orqaga",
        "en": "🔙 Back",
        "ru": "🔙 Назад"
    }

    await message.answer(
        success[lang],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=back[lang], callback_data="back")]]
        )
    )

    await state.clear()

@dp.message(lambda message: message.reply_to_message)
async def handle_admin_reply(message: types.Message):
    reply_msg_id = message.reply_to_message.message_id

    # SQLite'dan user_id va language ni olish
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, language FROM user_messages
        WHERE admin_msg_id = ?
    """, (reply_msg_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user_id = row["user_id"]
        username = row["username"]
        lang = row["language"] or "uz"

        # Foydalanuvchiga yuboriladigan matn
        text_translations = {
            "uz": f"📬 Admin javobi:\n\n{message.text}",
            "en": f"📬 Admin's reply:\n\n{message.text}",
            "ru": f"📬 Ответ администратора:\n\n{message.text}"
        }
        reply_text = text_translations.get(lang, text_translations["uz"])

        # 1️⃣ Foydalanuvchiga yuborish
        try:
            await message.bot.send_message(user_id, reply_text)
            await message.reply("✅ Javob foydalanuvchiga yuborildi.")
        except Exception as e:
            print(e)
            await message.reply("❌ Foydalanuvchiga yuborilmadi. Ehtimol, bloklangan.")

        # 2️⃣ Kanalga yuborish (tartibli format)
        try:
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            date_str = now.strftime("%d.%m.%Y")
            admin_username = message.from_user.username or "admin"

            channel_text = (
                f"[{time_str} {date_str}] @{admin_username} Javob berdi\n"
                f"To: @{username}\n"
                f"📬 Javob: {message.text}"
            )

            await message.bot.send_message(
                chat_id=CHANNEL_ID,
                text=channel_text
            )
        except Exception as e:
            print(f"❌ Kanalga yuborilmadi: {e}")

    else:
        await message.reply("⚠️ Bu javob bilan bog‘liq foydalanuvchi topilmadi.")
@dp.callback_query(F.data == "call_centr")
async def handle_call_center(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    text = {
        "uz": (
            "📞 *Acharya Universiteti Call Center*\n\n"
            "📱 Telefon: [ +998 55 301 00 09 ](tel:+998553010009)\n"
            "✉️ Email: info@acharya.uz\n"
            "🌐 Veb-sayt: [acharya.uz](https://acharya.uz)\n\n"
            "🏛 *Manzil:*\n"
            "Qorako‘l tumani, Buxoro viloyati, O‘zbekiston\n"
            "🔗 [📍 Google xaritada ochish](https://maps.app.goo.gl/qMqyfCNiGaowgFfs5)\n\n"
            "💡 Har qanday savollar bo‘lsa, biz bilan bemalol bog‘laning!"
        ),
        "en": (
            "📞 *Acharya University Call Center*\n\n"
            "📱 Phone: [ +998 55 301 00 09 ](tel:+998553010009)\n"
            "✉️ Email: info@acharya.uz\n"
            "🌐 Website: [acharya.uz](https://acharya.uz)\n\n"
            "🏛 *Address:*\n"
            "Qorako‘l district, Bukhara region, Uzbekistan\n"
            "🔗 [📍 Open in Google Maps](https://maps.app.goo.gl/qMqyfCNiGaowgFfs5)\n\n"
            "💡 If you have any questions, feel free to reach us!"
        ),
        "ru": (
            "📞 *Колл-центр Университета Ачарья*\n\n"
            "📱 Телефон: [ +998 55 301 00 09 ](tel:+998553010009)\n"
            "✉️ Email: info@acharya.uz\n"
            "🌐 Веб-сайт: [acharya.uz](https://acharya.uz)\n\n"
            "🏛 *Адрес:*\n"
            "Коракульский район, Бухарская область, Узбекистан\n"
            "🔗 [📍 Открыть в Google Картах](https://maps.app.goo.gl/qMqyfCNiGaowgFfs5)\n\n"
            "💡 Если у вас есть вопросы, звоните или пишите нам!"
        )
    }

    photo_url = "https://static.tildacdn.com/tild6537-3636-4063-b966-636661626330/6.jpg"

    await call.message.answer_photo(
        photo=photo_url,
        caption=text[lang],
        reply_markup=back_button(lang),
        parse_mode="Markdown"
    )

    try:
        await call.message.delete()
    except Exception:
        pass
@dp.callback_query(F.data == "developer")
async def handle_developer(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    messages = {
        "uz": (
            "👨‍💻 Dasturchi: Ushbu bot Axrorjon Ibrohimjonov tomonidan ishlab chiqildi.\n\n"
            "💡 Men Axrorjon Ibrohimjonov, Python/Django va Telegram botlar, shuningdek, veb dasturlar ustida ishlayman.\n"
            "🎓 Hozirda Acharya Universiteti, 2-kurs talabasi.\n"
            "🔗 Quyidagi havolalar orqali bog‘lanishingiz mumkin:"
        ),
        "en": (
            "👨‍💻 Developer: This bot was developed by Axrorjon Ibrohimjonov.\n\n"
            "💡 I am Axrorjon Ibrohimjonov, working on Python/Django, Telegram bots, and web apps.\n"
            "🎓 Currently a 2nd-year student at Acharya University.\n"
            "🔗 You can connect with me through the links below:"
        ),
        "ru": (
            "👨‍💻 Разработчик: Этот бот был разработан Ахрорбеком Иброхимжоновым.\n\n"
            "💡 Я Ахрорбек Иброхимжонов — работаю с Python/Django, Telegram-ботами и веб-приложениями.\n"
            "🎓 В настоящее время студент 2 курса Acharya University.\n"
            "🔗 Связаться со мной можно по ссылкам ниже:"
        ),
    }

    smart_quote = {
        "uz": "🚀 \"Kod yozish bu — g‘oyalarni haqiqatga aylantirish san’ati.\"",
        "en": "🚀 \"Programming is the art of turning ideas into reality.\"",
        "ru": "🚀 \"Программирование — это искусство превращения идей в реальность.\""
    }

    # Lokal rasm
    photo = "https://axrorback.github.io/profile.jpg"  # link orqali rasm

    # Tugmalar
    buttons = [
        [InlineKeyboardButton(text="💬 Telegram", url="https://t.me/axrorback")],
        [InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/axrorback")],
        [InlineKeyboardButton(text="👨‍💻 Web page", url="https://softwareuz.github.io")],
        [InlineKeyboardButton(text="🌐 Google Dev Account", url="https://g.dev/axrorback")],
        [InlineKeyboardButton(text="🔙 " + ("Orqaga" if lang == "uz" else "Back" if lang == "en" else "Назад"), callback_data="back")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.answer_photo(
        photo=photo,
        caption=f"{messages[lang]}\n\n{smart_quote[lang]}",
        reply_markup=keyboard
    )

    # Avvalgi xabarni o'chirish
    try:
        await call.message.delete()
    except Exception:
        pass

def admin_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Foydalanuvchilar ro‘yxati", callback_data="admin_users")],
        [InlineKeyboardButton(text="📢 Broadcast yuborish", callback_data="admin_broadcast")],
    ])

async def is_admin(tg_id: int) -> bool:
    def query():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admins WHERE telegram_id = ?", (tg_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    result = await asyncio.to_thread(query)
    return result is not None

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return await message.answer("❌ Sizda admin panelga ruxsat yo‘q.")

    await message.answer("👨‍💼 Admin panelga xush kelibsiz!\nNimani ko‘rishni istaysiz?", reply_markup=admin_menu_keyboard())

@dp.callback_query(F.data == "admin_users")
async def show_users(call: types.CallbackQuery):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY joined_at DESC")
    users = cursor.fetchall()
    conn.close()

    if not users:
        return await call.message.answer("👥 Hech qanday foydalanuvchi topilmadi.")

    text = "📋 <b>Foydalanuvchilar ro‘yxati:</b>\n\n"
    for user in users:
        username = f"@{user['username']}" if user['username'] else "—"
        text += (
            f"🧑‍💻 {user['full_name']} ({username})\n"
            f"🆔 {user['telegram_id']}\n"
            f"🌐 Til: {user['language']}\n"
            f"🕒 {user['joined_at']}\n\n"
        )

    await call.message.answer(text, parse_mode="HTML")
class BroadcastState(StatesGroup):
    waiting_for_text = State()
# Boshlash broadcast
@dp.callback_query(lambda c: c.data == "admin_broadcast")
async def start_broadcast(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        return await call.message.answer("⛔ Siz admin emassiz.")

    await call.message.answer("📨 Yubormoqchi bo‘lgan xabaringizni yuboring:")
    await state.set_state(BroadcastState.waiting_for_text)


# Xabar yuborish
@dp.message(BroadcastState.waiting_for_text)
async def send_broadcast(msg: types.Message, state: FSMContext):
    await state.clear()
    text = msg.text

    # SQLite'dan barcha telegram_id larni olish
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    users = cursor.fetchall()
    conn.close()

    success, failed = 0, 0
    for user in users:
        try:
            await bot.send_message(chat_id=user["telegram_id"], text=text)
            success += 1
        except Exception:
            failed += 1

    await msg.answer(f"✅ Yuborildi: {success} ta\n❌ Yuborilmadi: {failed} ta")


def back_button(language):
    back_text = {
        "uz": "🔙 Orqaga",
        "en": "🔙 Back",
        "ru": "🔙 Назад"
    }
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=back_text[language], callback_data="back")]
        ]
    )

@dp.callback_query(F.data == "check_status")
async def handle_check_status(call: types.CallbackQuery):
    lang = user_language.get(call.from_user.id, "uz")

    # DB dan so‘rov (SQLite misolida)
    conn = sqlite3.connect("bot_database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM applications WHERE telegram_id = ? ORDER BY id DESC LIMIT 1", (call.from_user.id,))
    app = cur.fetchone()
    conn.close()

    # Tugma (har doim chiqadi)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text={"uz": "🔙 Orqaga", "en": "🔙 Back", "ru": "🔙 Назад"}[lang],
                callback_data="back"
            )]
        ]
    )

    if not app:
        texts = {
            "uz": "❌ Sizning nomingizga ariza topilmadi.",
            "en": "❌ No application found for you.",
            "ru": "❌ Заявка не найдена."
        }
        await call.message.answer(texts[lang], reply_markup=keyboard)
        return

    # Javob matni
    caption = {
        "uz": (
            f"📋 **Ariza holati**\n\n"
            f"👤 Ism: {app['full_name']}\n"
            f"📞 Telefon: {app['phone']}\n"
            f"🏫 Fakultet: {app['faculty']}\n"
            f"🆔 Ariza raqami: {app['application_number']}\n"
            f"📌 Holat: {app['status']}"
        ),
        "en": (
            f"📋 **Application Status**\n\n"
            f"👤 Name: {app['full_name']}\n"
            f"📞 Phone: {app['phone']}\n"
            f"🏫 Faculty: {app['faculty']}\n"
            f"🆔 Application No: {app['application_number']}\n"
            f"📌 Status: {app['status']}"
        ),
        "ru": (
            f"📋 **Статус заявки**\n\n"
            f"👤 Имя: {app['full_name']}\n"
            f"📞 Телефон: {app['phone']}\n"
            f"🏫 Факультет: {app['faculty']}\n"
            f"🆔 Номер заявки: {app['application_number']}\n"
            f"📌 Статус: {app['status']}"
        )
    }

    await call.message.answer(caption[lang], parse_mode="Markdown", reply_markup=keyboard)






async def main():
    dp.startup.register(set_bot_menu)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())