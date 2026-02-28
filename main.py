import telebot
import requests
import sqlite3
import os

# --- اطلاعات جدید شما با دقت جایگذاری شد ---
API_TOKEN = '8751256075:AAEn2QOEJMeLFytHxU7Ryjz-e1UB5cpjPDg'
# آدرس دقیق ورکر شما طبق درخواست شما با /panel در انتها
PANEL_URL = 'https://nyje6ft2780hgve7x6h3facin4hy7gsj.zeuos-cfz00.workers.dev/panel' 
ADMIN_PASSWORD = 'Mosh3144' 

bot = telebot.TeleBot(API_TOKEN)

# تنظیمات دیتابیس برای جلوگیری از دریافت مجدد
db_path = os.path.join(os.path.dirname(__file__), 'users.db')
def init_db():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    return conn

conn = init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 دریافت کانفیگ ۴ گیگابایتی")
    bot.send_message(message.chat.id, "🚀 خوش آمدید! برای دریافت هدیه روی دکمه زیر کلیک کنید:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎁 دریافت کانفیگ ۴ گیگابایتی")
def give_config(message):
    user_id = message.from_user.id
    cursor = conn.cursor()
    
    # بررسی اینکه کاربر قبلاً هدیه گرفته است یا خیر
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    if cursor.fetchone():
        bot.reply_to(message, "❌ هر کاربر فقط یک‌بار می‌تواند هدیه دریافت کند.")
        return

    msg_wait = bot.send_message(message.chat.id, "⏳ در حال برقراری ارتباط با پنل...")

    try:
        # ارسال پارامترها به آدرس حاوی /panel
        params = {
            'password': ADMIN_PASSWORD,
            'action': 'add_user',
            'id': user_id,
            'limit': '4GB'
        }
        
        # درخواست GET به لینک ورکر
        response = requests.get(PANEL_URL, params=params, timeout=15)
        
        if response.status_code == 200 and "vless://" in response.text:
            config_link = response.text.strip()
            bot.delete_message(message.chat.id, msg_wait.message_id)
            bot.send_message(message.chat.id, f"✅ کانفیگ شما ساخته شد:\n\n`{config_link}`", parse_mode="Markdown")
            
            # ثبت در دیتابیس
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
        else:
            # نمایش خطا در صورت دریافت پاسخ HTML یا خطای دیگر
            error_msg = "پاسخ نامعتبر (HTML)" if "<!DOCTYPE" in response.text else response.text[:50]
            bot.edit_message_text(f"⚠️ پنل پاسخ نداد:\n{error_msg}", message.chat.id, msg_wait.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ خطای هاست: PythonAnywhere اجازه اتصال به ورکر را نمی‌دهد.", message.chat.id, msg_wait.message_id)

if __name__ == "__main__":
    print("Bot is running with /panel URL...")
    bot.infinity_polling()
