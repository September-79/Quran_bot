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

def to_arabic_num(n):
    arabic = "٠١٢٣٤٥٦٧٨٩"
    return "".join(arabic[int(d)] for d in str(n))

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
            r = requests.get("https://api.alquran.cloud/v1/ayah/random/quran-uthmani").json()
            ayah = r['data']
            await update.message.reply_text(f"{ayah['text']} ﴿{to_arabic_num(ayah['numberInSurah'])}﴾\n\n— سورة {ayah['surah']['name']}")
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

        msg = await update.message.reply_text(f"لقد اخترت سورة {text} من القارئ {reciter_name} برواية حفص عن عاصم، جاري التحميل ..")

        # 1 - نص السورة بالشكل الجديد - تقسيم ذكي
        try:
            data = requests.get(f"https://api.alquran.cloud/v1/surah/{n}/quran-uthmani").json()['data']
            ayahs = data['ayahs']

            header = f"✦ ━━━━ سورة {text} ━━━━ ✦\n\n"
            if n != 9:
                header += "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ\n\n"
            footer = "\n\n━━━ صدق الله العظيم ━━━"

            # تقسيم ذكي: بنجمع الآيات آية آية، ومنقطعش في نص الآية أبدا
            chunks = []
            current = header
            for a in ayahs:
                t = a['text']
                if a['numberInSurah'] == 1 and n not in [1, 9]:
                    t = t.replace("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "").strip()
                line = f"{t} ﴿{to_arabic_num(a['numberInSurah'])}﴾ "
                # لو الرسالة هتعدي 3800 حرف، نقفلها ونبدأ رسالة جديدة
                if len(current) + len(line) > 3800:
                    chunks.append(current)
                    current = ""
                current += line
            current += footer
            chunks.append(current)

            for idx, chunk in enumerate(chunks, 1):
                if len(chunks) > 1:
                    await update.message.reply_text(f"— جزء {idx}/{len(chunks)} —\n\n{chunk}")
                else:
                    await update.message.reply_text(chunk)
        except Exception as e:
            await update.message.reply_text("حصلت مشكلة في تحميل النص، حاول تاني")

        # 2 - صوت السورة كامل - من غير زر فتح المصحف
        audio_url = f"https://cdn.islamic.network/quran/audio-surah/128/{code}/{n}.mp3"
        await update.message.reply_audio(
            audio=audio_url,
            title=text,
            performer=reciter_name,
            caption=f"🎧 سورة {text} - {reciter_name}"
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

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reciter_callback, pattern="^reciter:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot is running...")
    app.run_polling()
