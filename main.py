import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","ابراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الانسان","المرسلات","النبأ","النازعات","عبس","التكوير","الإنفطار","المطففين","الإنشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

SURAH_INFO = {
    "الفاتحة": {"virtue": "أعظم سورة في القرآن، وهي السبع المثاني، لا تصح الصلاة إلا بها.", "reason": "نزلت بمكة، وهي أول سورة كاملة نزلت."},
    "البقرة": {"virtue": "أخذها بركة وتركها حسرة، ولا تستطيعها البطلة (السحرة). فيها آية الكرسي أعظم آية.", "reason": "نزلت بالمدينة، وهي أول سورة نزلت بالمدينة."},
    "آل عمران": {"virtue": "تأتي يوم القيامة تحاج عن صاحبها مع البقرة كأنهما غمامتان.", "reason": "نزلت بالمدينة بعد غزوة أحد."},
    "الكهف": {"virtue": "من قرأها يوم الجمعة أضاء له من النور ما بين الجمعتين، وعصم من فتنة الدجال.", "reason": "نزلت بمكة لما سأل المشركون عن أهل الكهف."},
    "يس": {"virtue": "قلب القرآن، من قرأها كتب له بقراءتها قراءة القرآن عشر مرات.", "reason": "نزلت بمكة."},
    "الرحمن": {"virtue": "عروس القرآن، فيها تكرار فبأي آلاء ربكما تكذبان.", "reason": "نزلت بالمدينة، وقيل مكية."},
    "الواقعة": {"virtue": "من قرأها كل ليلة لم تصبه فاقة أبدا، وهي سورة الغنى.", "reason": "نزلت بمكة."},
    "الملك": {"virtue": "سورة تشفع لصاحبها، من قرأها كل ليلة منجية من عذاب القبر.", "reason": "نزلت بمكة."},
    "الإخلاص": {"virtue": "تعدل ثلث القرآن، من قرأها 3 مرات كأنما قرأ القرآن كله.", "reason": "نزلت بمكة لما سأل المشركون: صف لنا ربك."},
    "الفلق": {"virtue": "من المعوذتين، ما تعوذ متعوذ بمثلهما.", "reason": "نزلت بمكة، وقيل بالمدينة."},
    "الناس": {"virtue": "من المعوذتين، خاتمة القرآن، تحفظ من وسوسة الشيطان.", "reason": "نزلت بمكة، وقيل بالمدينة."},
    "الكوثر": {"virtue": "فيها إنا أعطيناك الكوثر، وهو نهر في الجنة.", "reason": "نزلت بمكة."},
    "الكافرون": {"virtue": "تعدل ربع القرآن، وهي براءة من الشرك.", "reason": "نزلت بمكة."},
    "النصر": {"virtue": "تعدل ربع القرآن، وهي آخر سورة نزلت كاملة.", "reason": "نزلت بالمدينة في حجة الوداع."},
    "القدر": {"virtue": "ليلة القدر خير من ألف شهر.", "reason": "نزلت بمكة."},
    "الفاتحة": {"virtue": "أعظم سورة في القرآن.", "reason": "نزلت بمكة."},
}

AZKAR_SABAH = [
    "🌅 أذكار الصباح\n━━━━━━━━━━\n\n1- آية الكرسي: {اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ} (مرة واحدة)",
    "2- قل هو الله أحد + الفلق + الناس (3 مرات لكل سورة)\n\n﴿ قُلْ هُوَ اللَّهُ أَحَدٌ ﴾",
    "3- أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له (مرة واحدة)",
    "4- سبحان الله وبحمده (100 مرة)\nمن قالها حطت خطاياه وإن كانت مثل زبد البحر",
    "5- اللهم بك أصبحنا وبك أمسينا وبك نحيا وبك نموت وإليك النشور (مرة واحدة)",
    "6- يا حي يا قيوم برحمتك أستغيث أصلح لي شأني كله ولا تكلني إلى نفسي طرفة عين (مرة واحدة)",
    "7- اللهم إني أسألك علماً نافعاً ورزقاً طيباً وعملاً متقبلاً (مرة واحدة)",
    "8- أستغفر الله وأتوب إليه (100 مرة)",
]

AZKAR_MASA = [
    "🌙 أذكار المساء\n━━━━━━━━━━\n\n1- آية الكرسي: {اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ} (مرة واحدة)",
    "2- قل هو الله أحد + الفلق + الناس (3 مرات لكل سورة)",
    "3- أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له (مرة واحدة)",
    "4- سبحان الله وبحمده (100 مرة)",
    "5- اللهم بك أمسينا وبك أصبحنا وبك نحيا وبك نموت وإليك المصير (مرة واحدة)",
    "6- أعوذ بكلمات الله التامات من شر ما خلق (3 مرات)",
    "7- بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم (3 مرات)",
    "8- اللهم إني أسألك العفو والعافية في الدنيا والآخرة (مرة واحدة)",
]

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
        [KeyboardButton("📖 تفسير السورة"), KeyboardButton("🔍 بحث باسم السورة")],
        [KeyboardButton("🌅 أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
        [KeyboardButton("⏰ تذكير سورة الملك"), KeyboardButton("❌ إلغاء التذكير")],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بيك في بوت القرآن الكريم 🤍\nاختر من القائمة:",
        reply_markup=main_keyboard()
    )

# وظيفة التذكير اليومي - سورة الملك الساعة 10 مساء
async def send_mulk_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    try:
        await context.bot.send_message(chat_id=chat_id, text="⏰ وقتك مع سورة الملك 🤍\n\nمن قرأها كل ليلة منجية من عذاب القبر، يلا نقرأها سوا قبل النوم:")
        data = requests.get("https://api.alquran.cloud/v1/surah/67/quran-uthmani").json()['data']
        full = ""
        for a in data['ayahs']:
            full += f"{a['text']} ﴿{to_arabic_num(a['numberInSurah'])}﴾ "
        header = "✦ ━━━━ سورة الملك ━━━━ ✦\n\nبِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ\n\n"
        footer = "\n\n━━━ صدق الله العظيم ━━━"
        text = header + full + footer
        for i in range(0, len(text), 3800):
            await context.bot.send_message(chat_id=chat_id, text=text[i:i+3800])
        await context.bot.send_audio(chat_id=chat_id, audio="https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/67.mp3", title="الملك", performer="عبدالباسط عبدالصمد", caption="🎧 سورة الملك - تذكير يومي")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="وقت سورة الملك 🤍\nافتحها من هنا: https://quran.com/67")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if text == "🏠 القائمة الرئيسية":
        context.user_data['mode'] = None
        await update.message.reply_text("القائمة الرئيسية:", reply_markup=main_keyboard())
        return

    if text in ["🎧 الاستماع للقرآن", "📖 قراءة السورة", "🔍 بحث باسم السورة"]:
        context.user_data['mode'] = 'read'
        await update.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

    if text == "📖 تفسير السورة":
        context.user_data['mode'] = 'tafsir'
        await update.message.reply_text("اختر السورة اللي عايز تفسيرها 👇", reply_markup=surah_keyboard())
        return

    if text == "🎙️ تغيير القارئ":
        kb = [[InlineKeyboardButton(name, callback_data=f"reciter:{code}")] for name, code in RECITERS.items()]
        await update.message.reply_text("اختر القارئ:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == "🌅 أذكار الصباح":
        for z in AZKAR_SABAH:
            await update.message.reply_text(z)
        return

    if text == "🌙 أذكار المساء":
        for z in AZKAR_MASA:
            await update.message.reply_text(z)
        return

    if text == "⏰ تذكير سورة الملك":
        try:
            # شيل أي تذكير قديم الأول
            current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
            for j in current_jobs:
                j.schedule_removal()
            # كل يوم الساعة 22:00 بتوقيت مصر
            import datetime
            context.job_queue.run_daily(send_mulk_reminder, time=datetime.time(hour=22, minute=0), chat_id=chat_id, name=str(chat_id))
            await update.message.reply_text("✅ تم تفعيل التذكير اليومي!\n\nكل يوم الساعة 10 مساء هبعتلك سورة الملك كاملة نص + صوت قبل النوم 🤍\n\nلو حابب تلغيه دوس ❌ إلغاء التذكير")
        except Exception as e:
            await update.message.reply_text("التذكير مش شغال في الاستضافة دي، جرب تاني بعد شوية")
        return

    if text == "❌ إلغاء التذكير":
        try:
            jobs = context.job_queue.get_jobs_by_name(str(chat_id))
            for j in jobs:
                j.schedule_removal()
            await update.message.reply_text("تم إلغاء تذكير سورة الملك ❌")
        except:
            await update.message.reply_text("مفيش تذكير شغال حاليا")
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
        mode = context.user_data.get('mode', 'read')
        code = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        reciter_name = "عبدالباسط عبدالصمد"
        for k, v in RECITERS.items():
            if v == code:
                reciter_name = k

        # ===== وضع التفسير =====
        if mode == 'tafsir':
            await update.message.reply_text(f"جاري تحميل تفسير سورة {text} 📖 ...")
            try:
                # النص الأصلي + التفسير الميسر
                orig = requests.get(f"https://api.alquran.cloud/v1/surah/{n}/quran-uthmani").json()['data']['ayahs']
                tafsir = requests.get(f"https://api.alquran.cloud/v1/surah/{n}/ar.muyassar").json()['data']['ayahs']
                for o, t in zip(orig, tafsir):
                    msg_tafsir = f"﴿{o['text']}﴾ ﴿{to_arabic_num(o['numberInSurah'])}﴾\n\n📖 التفسير:\n{t['text']}"
                    await update.message.reply_text(msg_tafsir)
                await update.message.reply_text("━━━ انتهى تفسير سورة " + text + " ━━━", reply_markup=main_keyboard())
            except:
                await update.message.reply_text("حصلت مشكلة في التفسير، حاول تاني")
            context.user_data['mode'] = 'read'
            return

        # ===== وضع القراءة العادي =====
        msg = await update.message.reply_text(f"لقد اخترت سورة {text} من القارئ {reciter_name} برواية حفص عن عاصم، جاري التحميل ..")
        try:
            data = requests.get(f"https://api.alquran.cloud/v1/surah/{n}/quran-uthmani").json()['data']
            ayahs = data['ayahs']
            revelation = data.get('revelationType', '')
            if revelation == 'Meccan':
                revelation_ar = "مكية 🕋"
            elif revelation == 'Medinan':
                revelation_ar = "مدنية 🕌"
            else:
                revelation_ar = revelation
            num_ayahs = data.get('numberOfAyahs', len(ayahs))
            english_name = data.get('englishName', '')
            info = SURAH_INFO.get(text, {})
            virtue = info.get('virtue', 'سورة من سور القرآن الكريم، فيها الهدى والنور والشفاء.')
            reason = info.get('reason', 'نزلت على النبي ﷺ هدى للناس وبينات من الهدى والفرقان.')
            info_text = (
                f"📋 معلومات عن سورة {text}:\n"
                f"━━━━━━━━━━━━━━\n"
                f"• النوع: {revelation_ar}\n"
                f"• عدد الآيات: {num_ayahs} آية\n"
                f"• ترتيبها في المصحف: {n}\n"
                f"• اسمها بالإنجليزية: {english_name}\n"
                f"• القارئ: {reciter_name}\n\n"
                f"🌟 فضلها:\n{virtue}\n\n"
                f"📖 سبب نزولها:\n{reason}"
            )
            await update.message.reply_text(info_text)
            header = f"✦ ━━━━ سورة {text} ━━━━ ✦\n\n"
            if n != 9:
                header += "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ\n\n"
            footer = "\n\n━━━ صدق الله العظيم ━━━"
            chunks = []
            current = header
            for a in ayahs:
                t = a['text']
                if a['numberInSurah'] == 1 and n not in [1, 9]:
                    t = t.replace("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "").strip()
                line = f"{t} ﴿{to_arabic_num(a['numberInSurah'])}﴾ "
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
