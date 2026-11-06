import os, requests, telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

FORCE_CHANNEL = "@SEPTEMBER_Movies_TV_shows"
FORCE_CHANNEL_LINK = "https://t.me/SEPTEMBER_Movies_TV_shows"

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return m.status in ("member", "administrator", "creator")
    except:
        return False

def send_subscribe_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك في القناة", url=FORCE_CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("✅ اشتركت - تحقق", callback_data="check_sub"))
    bot.send_message(chat_id, "📢 لازم تشترك في قناتنا عشان تستخدم بوت القرآن 👇", reply_markup=markup)

# جلب أسماء السور
def get_surahs():
    try:
        r = requests.get("https://api.alquran.cloud/v1/surah", timeout=15).json()
        return r["data"]
    except:
        return []

@bot.message_handler(commands=["start"])
def start(m):
    if not is_subscribed(m.from_user.id):
        send_subscribe_msg(m.chat.id)
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📖 قراءة سورة", callback_data="read_list"))
    markup.add(types.InlineKeyboardButton("🎧 سماع سورة", callback_data="audio_list"))
    markup.add(types.InlineKeyboardButton("📿 آية اليوم", callback_data="daily"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_help"))
    bot.reply_to(m, "🕋 أهلاً بيك في بوت القرآن الكريم\n\nاختار 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def on_btn(c):
    if c.data == "check_sub":
        if is_subscribed(c.from_user.id):
            bot.edit_message_text("✅ تمام اشتركت، دوس /start", c.message.chat.id, c.message.message_id)
        else:
            bot.answer_callback_query(c.id, "❌ لسه مش مشترك", show_alert=True)
        return
    if not is_subscribed(c.from_user.id):
        send_subscribe_msg(c.message.chat.id)
        return
    if c.data == "daily":
        try:
            r = requests.get("https://api.alquran.cloud/v1/ayah/2:255", timeout=10).json()
            ayah = r["data"]["text"]
            bot.send_message(c.message.chat.id, f"📿 آية الكرسي:\n\n{ayah}\n\nصدق الله العظيم")
        except:
            bot.send_message(c.message.chat.id, "❌ حصل خطأ حاول تاني")
        return
    if c.data in ("read_list", "audio_list"):
        surahs = get_surahs()
        markup = types.InlineKeyboardMarkup()
        # أول 30 سورة كمثال - عشان الأزرار متبقاش كتير
        for s in surahs[:30]:
            mode = "read" if c.data=="read_list" else "audio"
            markup.add(types.InlineKeyboardButton(f"{s['number']} - {s['name']}", callback_data=f"{mode}:{s['number']}"))
        markup.add(types.InlineKeyboardButton("➡️ باقي السور", callback_data=f"{c.data}_2"))
        bot.edit_message_text("اختار السورة 👇", c.message.chat.id, c.message.message_id, reply_markup=markup)
        return
    if c.data.startswith("read:"):
        num = c.data.split(":")[1]
        bot.edit_message_text(f"⏳ بجيب سورة {num}...", c.message.chat.id, c.message.message_id)
        try:
            r = requests.get(f"https://api.alquran.cloud/v1/surah/{num}", timeout=15).json()
            surah = r["data"]
            text = f"بسم الله الرحمن الرحيم\n\n"
            for ayah in surah["ayahs"][:10]:  # أول 10 آيات عشان رسالة تليجرام
                text += f"{ayah['text']} ﴿{ayah['numberInSurah']}﴾\n"
            text += f"\n... سورة {surah['name']} - {surah['numberOfAyahs']} آية"
            bot.send_message(c.message.chat.id, text)
        except:
            bot.send_message(c.message.chat.id, "❌ حصل خطأ")
        return
    if c.data.startswith("audio:"):
        num = c.data.split(":")[1]
        bot.edit_message_text("⏳ بحمّل الصوت...", c.message.chat.id, c.message.message_id)
        try:
            # صوت مشاري راشد
            audio_url = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{num}.mp3"
            bot.send_audio(c.message.chat.id, audio_url, caption=f"🎧 سورة {num} - مشاري راشد العفاسي")
        except:
            bot.send_message(c.message.chat.id, "❌ مش قادر أجيب الصوت")
        return

@bot.message_handler(func=lambda m: True)
def handle(m):
    if not is_subscribed(m.from_user.id):
        send_subscribe_msg(m.chat.id)
        return
    text = (m.text or "").strip()
    surahs = get_surahs()
    for s in surahs:
        if text in s["name"] or text in s["englishName"] or text == str(s["number"]):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📖 قراءة", callback_data=f"read:{s['number']}"))
            markup.add(types.InlineKeyboardButton("🎧 سماع", callback_data=f"audio:{s['number']}"))
            bot.reply_to(m, f"سورة {s['name']} - {s['numberOfAyahs']} آية\nاختار 👇", reply_markup=markup)
            return
    bot.reply_to(m, "اكتب اسم السورة زي `يس` أو `البقرة` أو رقمها، أو دوس /start")

print("QURAN BOT READY")
bot.infinity_polling()
