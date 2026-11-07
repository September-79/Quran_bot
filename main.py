import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","ابراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الانسان","المرسلات","النبأ","النازعات","عبس","التكوير","الإنفطار","المطففين","الإنشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

RECITERS = {
    "عبدالباسط عبدالصمد": "ar.abdulbasitmurattal",
    "مشاري راشد العفاسي": "ar.alafasy",
    "محمود خليل الحصري": "ar.husary",
    "سعد الغامدي": "ar.aymanswoaid",
    "محمد المنشاوي": "ar.minshawi",
}

user_reciter = {}

def surah_keyboard():
    rows = []
    for i in range(0, len(SURAHS), 4):
        rows.append([KeyboardButton(s) for s in SURAHS[i:i+4]])
    rows.append([KeyboardButton("🏠 القائمة الرئيسية")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎧 الاستماع للقرآن"), KeyboardButton("📖 قراءة السورة")],
        [KeyboardButton("🎙️ تغيير القارئ"), KeyboardButton("📿 آية اليوم")],
        [KeyboardButton("🔍 بحث باسم السورة")],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بيك في بوت القرآن الكريم 🤍\nاختر من القائمة:",
        reply_markup=main_keyboard()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🏠 القائمة الرئيسية":
        await update.message.reply_text("القائمة الرئيسية:", reply_markup=main_keyboard())
        return

    if text in ["🎧 الاستماع للقرآن", "📖 قراءة السورة", "🔍 بحث باسم السورة"]:
        await update.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

    if text == "🎙️ تغيير القارئ":
        kb = [[InlineKeyboardButton(name, callback_data=f"reciter:{code}")] for name, code in RECITERS.items()]
        await update.message.reply_text("اختر القارئ:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == "📿 آية اليوم":
        try:
            r = requests.get("https://api.alquran.cloud/v1/ayah/random").json()
            ayah = r['data']
            await update.message.reply_text(f"{ayah['text']}\n\n— {ayah['surah']['name']} - آية {ayah['numberInSurah']}")
        except:
            await update.message.reply_text("حاول تاني")
        return

    if text in SURAHS:
        n = SURAHS.index(text) + 1
        code = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        reciter_name = "عبدالباسط عبدالصمد"
        for k, v in RECITERS.items():
            if v == code:
                reciter_name = k

        msg = await update.message.reply_text(f"لقد اخترت سورة {text} من القارئ {reciter_name} برواية حفص عن عاصم - المصحف الموجود , ستتصل لك في لحظات ..")

        try:
            data = requests.get(f"https://api.alquran.cloud/v1/surah/{n}").json()['data']
            full_text = "\n".join([f"{a['text']} ﴿{a['numberInSurah']}﴾" for a in data['ayahs']])
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(f"سورة {text}\n\n{full_text[i:i+4000]}")
        except:
            pass

        audio_url = f"https://cdn.islamic.network/quran/audio-surah/128/{code}/{n}.mp3"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("فتح المصحف 📖", callback_data=f"mushaf:{n}")]])
        await update.message.reply_audio(
            audio=audio_url,
            title=text,
            performer=reciter_name,
            caption=f"🎧 سورة {text} - {reciter_name}",
            reply_markup=keyboard
        )
        await msg.delete()
        return

    await update.message.reply_text("اكتب اسم سورة صحيح أو اختر من القائمة 👇", reply_markup=surah_keyboard())

async def reciter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.split(":")[1]
    user_reciter[query.from_user.id] = code
    name = [k for k,v in RECITERS.items() if v==code][0]
    await query.edit_message_text(f"تم اختيار القارئ: {name} ✅\nالآن اختر السورة:")
    await query.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())

async def mushaf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    n = int(query.data.split(":")[1])
    surah_name = SURAHS[n-1]
    await query.message.reply_text(f"جاري فتح مصحف سورة {surah_name} 📖 ...")
    try:
        data = requests.get(f"https://api.alquran.cloud/v1/surah/{n}").json()['data']
        ayahs = data['ayahs']
        # لو السورة طويلة زي البقرة مش هنبعت 286 صورة
        if len(ayahs) > 20:
            await query.message.reply_text(f"سورة {surah_name} طويلة، افتح المصحف كامل من هنا 👇\nhttps://quran.com/{n}")
            ayahs = ayahs[:10]
        for a in ayahs:
            ayah_num = a['numberInSurah']
            # اللينك الصح لصورة الآية بالرسم العثماني المزخرف
            img_url = f"https://cdn.islamic.network/quran/images/{n}_{ayah_num}.png"
            await query.message.reply_photo(photo=img_url, caption=f"سورة {surah_name} - آية {ayah_num}")
    except Exception as e:
        await query.message.reply_text(f"افتح المصحف من هنا: https://quran.com/{n}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reciter_callback, pattern="^reciter:"))
    app.add_handler(CallbackQueryHandler(mushaf_callback, pattern="^mushaf:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot is running...")
    app.run_polling()
