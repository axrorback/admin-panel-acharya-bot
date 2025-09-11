import io
import string
from datetime import datetime, timedelta
import random
from PIL import Image , ImageDraw , ImageFont
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3, requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key"

DB_NAME = "bot_database.db"
BOT_TOKEN = "8099179109:AAEHi2ZNiCW1xW2ESKsKFHeu2LfhH3r89us"   #
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
CHANNEL_ID = "-1003051981115"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ========== AUTH ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("Iltimos login qiling!", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["full_name"]
            flash("Xush kelibsiz!", "success")
            return redirect(url_for("users"))
        else:
            flash("❌ Login yoki parol noto‘g‘ri!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Chiqdingiz!", "info")
    return redirect(url_for("login"))


# ========== USERS ==========
@app.route("/")
@login_required
def users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("users.html", users=users)


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_profile(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not user:
        flash("❌ Bunday user yo‘q!", "danger")
        return redirect(url_for("users"))

    if request.method == "POST":
        message = request.form["message"]

        payload = {"chat_id": user["telegram_id"], "text": message}
        response = requests.post(f"{API_URL}/sendMessage", data=payload).json()

        if response.get("ok"):
            flash("✅ Xabar yuborildi!", "success")
        else:
            error_code = response.get("error_code")
            if error_code == 403:
                flash("❌ User botni bloklagan!", "danger")
            else:
                flash(f"❌ Xatolik: {response.get('description')}", "danger")

        return redirect(url_for("user_profile", user_id=user_id))

    return render_template("user_profile.html", user=user)


# ========== ADMINS ==========
@app.route("/admins")
@login_required
def admins():
    conn = get_db_connection()
    admins = conn.execute("SELECT * FROM admins ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admins.html", admins=admins)


# ========== MESSAGES ==========
@app.route("/messages")
@login_required
def messages():
    search = request.args.get("search", "")
    conn = get_db_connection()
    if search:
        msgs = conn.execute(
            "SELECT * FROM user_messages WHERE message_text LIKE ? ORDER BY id DESC",
            (f"%{search}%",),
        ).fetchall()
    else:
        msgs = conn.execute("SELECT * FROM user_messages ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("messages.html", messages=msgs, search=search)

@login_required
@app.route("/reply/<int:msg_id>", methods=["POST"])
def reply_message(msg_id):
    reply_text = request.form.get("reply_text")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, user_id FROM user_messages WHERE id = ?", (msg_id,))
    msg = cursor.fetchone()
    conn.close()

    if not msg:
        flash("❌ Message not found.", "danger")
        return redirect(url_for("messages"))

    payload = {
        "chat_id": msg["user_id"],
        "text": reply_text
    }

    try:
        response = requests.post(f"{API_URL}/sendMessage", data=payload).json()
        if response.get("ok"):
            flash(f"✅ Reply sent to @{msg['username']}", "success")
        else:
            if response.get("error_code") == 403:
                flash(f"❌ User @{msg['username']} botni bloklagan!", "danger")
            else:
                flash(f"❌ Xatolik: {response.get('description')}", "danger")
    except Exception as e:
        flash(f"❌ Xatolik yuz berdi: {str(e)}", "danger")

    return redirect(url_for("messages"))

# ===================== OTP GENERATOR =====================
def generate_otp(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    code = "".join(random.choices(string.digits, k=4))
    expires_at = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO otps (user_id, code, expires_at, is_used)
        VALUES (?, ?, ?, 0)
    """, (user_id, code, expires_at))
    otp_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return otp_id, code


# ===================== APPLICATION NUMBER =====================
def generate_application_number():
    year = datetime.now().year % 100
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM applications")
    total = cursor.fetchone()["total"] + 1
    conn.close()
    return f"AU/{year}/{str(total).zfill(4)}"


# ===================== CAPTCHA IMAGE =====================
@app.route("/captcha/<int:otp_id>.png")
def captcha_image(otp_id):
    conn = get_db_connection()
    otp = conn.execute("SELECT code FROM otps WHERE id = ?", (otp_id,)).fetchone()
    conn.close()

    if not otp:
        return "❌ OTP not found", 404

    code = otp["code"]

    # Rasm yaratish
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((50, 20), code, fill=(0, 0, 0), font=font)

    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")

# ===================== APPLY FORM =====================
@app.route("/apply", methods=["GET", "POST"])
def apply():
    faculties = [
        "Kompyuter injiniringi (B.Tech)",
        "Ma'lumotlar fani (B.Tech)",
        "Sun'iy intellekt (B.Tech)",
        "Bulutli hisoblash va xavfsizlik (B.Tech)",
        "Bulutli hisoblash (BCA)",
        "Axborot texnologiyalari (BCA)",
        "Ma'lumotlar tahlili (BCA)",
        "Fullstack Developer (BCA)",
        "UI & UX Dizayn (BCA)",
        "Biznes tahlili (BCA)",
        "Fintech (BCA)",
        "Raqamli marketing (BCA)"
    ]

    if request.method == "POST":
        # formdan kelgan qiymatlar
        name = request.form["name"]
        surname = request.form["surname"]
        full_name = f"{name} {surname}"

        phone = request.form["phone"]
        faculty = request.form["faculty"]
        otp_id = request.form["otp_id"]
        otp_code = request.form["captcha"]

        # OTP tekshirish
        conn = get_db_connection()
        otp = conn.execute("SELECT * FROM otps WHERE id = ? AND is_used = 0", (otp_id,)).fetchone()

        if not otp:
            flash("❌ OTP topilmadi!", "danger")
            return redirect(url_for("apply"))

        if datetime.strptime(otp["expires_at"], "%Y-%m-%d %H:%M:%S") < datetime.now():
            flash("❌ Kod muddati tugagan!", "danger")
            return redirect(url_for("apply"))

        if otp["code"] != otp_code:
            flash("❌ Kod noto‘g‘ri!", "danger")
            return redirect(url_for("apply"))

        # ✅ Arizani saqlash
        app_number = generate_application_number()
        conn.execute("""
            INSERT INTO applications (application_number, telegram_id, full_name, phone, faculty, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (app_number, otp["user_id"], full_name, phone, faculty, "Yangi"))

        conn.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (otp_id,))
        conn.commit()
        conn.close()

        # ✅ Telegram kanalga yuborish
        msg = (
            f"📑 Yangi ariza!\n\n"
            f"👤 Ism: {full_name}\n"
            f"📞 Telefon: {phone}\n"
            f"🏫 Fakultet: {faculty}\n"
            f"📋 Ariza raqami: {app_number}"
        )
        try:
            requests.post(f"{API_URL}/sendMessage", data={"chat_id": CHANNEL_ID, "text": msg})
        except:
            print("⚠️ Telegramga yuborilmadi")

        # ✅ Foydalanuvchining o‘ziga yuborish
        try:
            requests.post(f"{API_URL}/sendMessage", data={
                "chat_id": otp["user_id"],
                "text": f"✅ Sizning arizangiz qabul qilindi!\n\nAriza raqami: {app_number}"
            })
        except:
            print("⚠️ Foydalanuvchiga yuborilmadi")

        flash(f"✅ Arizangiz qabul qilindi! Sizning ariza raqamingiz: {app_number}", "success")
        return redirect(url_for("thanks", app_number=app_number.replace("/", "-")))

    # GET → form
    user_id = request.args.get("user_id")  # Bot link orqali yuboradi
    if not user_id:
        return "❌ User ID kerak!", 400

    otp_id, _ = generate_otp(user_id)
    return render_template("apply.html", faculties=faculties, otp_id=otp_id)

# ===================== THANKS PAGE =====================
@app.route("/thanks/<app_number>")
def thanks(app_number):
    real_number = app_number.replace("-", "/")

    return render_template("thanks.html", app_number=real_number)


# ========== APPLICATIONS ==========
@app.route("/applications")
@login_required
def applications():
    conn = get_db_connection()
    apps = conn.execute("""
        SELECT a.*
        FROM applications a
        ORDER BY a.id DESC
    """).fetchall()
    conn.close()
    return render_template("applications.html", applications=apps)

@app.route("/applications/<int:app_id>", methods=["GET", "POST"])
@login_required
def application_detail(app_id):
    conn = get_db_connection()
    app_data = conn.execute("""
        SELECT *
        FROM applications
        WHERE id = ?
    """, (app_id,)).fetchone()

    if not app_data:
        flash("❌ Bunday ariza topilmadi!", "danger")
        return redirect(url_for("applications"))

    if request.method == "POST":
        new_status = request.form.get("status")
        admin_note = request.form.get("admin_note", "")

        conn.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
        conn.commit()

        # ✅ Userga xabar yuborish
        try:
            msg = (
                f"📢 Salom!\n\n"
                f"📋 Sizning arizangiz ({app_data['application_number']}) holati yangilandi:\n"
                f"🟢 Holat: {new_status}\n\n"
            )
            if admin_note.strip():
                msg += f"✍️ Admin izohi: {admin_note}"

            requests.post(f"{API_URL}/sendMessage", data={
                "chat_id": app_data["telegram_id"],
                "text": msg
            })
        except Exception as e:
            print("⚠️ Telegramga yuborilmadi:", e)

        conn.close()
        flash("✅ Ariza holati yangilandi va foydalanuvchiga habar yuborildi!", "success")
        return redirect(url_for("application_detail", app_id=app_id))

    conn.close()
    return render_template("application_detail.html", app=app_data)
# ===================== DELETE APPLICATION =====================
@app.route("/applications/<int:app_id>/delete", methods=["POST"])
@login_required
def delete_application(app_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    flash("🗑️ Ariza o‘chirildi!", "warning")
    return redirect(url_for("applications"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def admin_profile():
    conn = get_db_connection()
    admin = conn.execute("SELECT * FROM admins WHERE id = ?", (session["admin_id"],)).fetchone()

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # ✅ Eski parolni tekshirish
        if not check_password_hash(admin["password_hash"], old_password):
            flash("❌ Eski parol noto‘g‘ri!", "danger")
            return redirect(url_for("admin_profile"))

        if new_password != confirm_password:
            flash("❌ Yangi parollar mos emas!", "danger")
            return redirect(url_for("admin_profile"))

        # ✅ Parolni yangilash
        hashed = generate_password_hash(new_password)
        conn.execute("UPDATE admins SET password_hash = ? WHERE id = ?", (hashed, session["admin_id"]))
        conn.commit()
        conn.close()

        # 🔐 Sessiyani tozalash va qayta login talab qilish
        session.clear()
        flash("✅ Parol muvaffaqiyatli yangilandi! Qayta login qiling.", "success")
        return redirect(url_for("login"))

    conn.close()
    return render_template("admin_profile.html", admin=admin)





if __name__ == "__main__":
    app.run(debug=True)
