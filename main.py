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
    "محمد رفعت": "ar.muhammadrafat",
}

RIFAAT_SURAHS = [
    "الفاتحة","البقرة","يونس","هود","يوسف","الإسراء","الكهف","مريم","طه",
    "الفتح","القمر","الرحمن","الواقعة","الحاقة","الجن","المزمل","القيامة",
    "الانسان","المرسلات","النبأ","النازعات","التكوير","الإنفطار","المطففين",
    "البروج","الطارق","الأعلى","الغاشية","الفجر","العلق","البينة","العاديات",
    "القارعة","التكاثر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون",
    "النصر","المسد","الإخلاص","الفلق","الناس","يس","الصافات","الدخان","الملك",
    "القلم","الحشر","الجمعة","التغابن","الطلاق","التحريم","نوح","المدثر","الضحى",
    "الشرح","التين","القدر","الزلزلة","العصر"
]

user_reciter = {}
user_city = {}

# ================= الشيخ محمد رفعت - من mp3quran API =================
_rifaat_cache = {}
_rifaat_server = None
_rifaat_available = None

def load_rifaat_from_api():
    global _rifaat_server, _rifaat_available
    if _rifaat_server is not None:
        return _rifaat_server, _rifaat_available
    try:
        r = requests.get("https://www.mp3quran.net/api/v3/reciters?language=ar", timeout=15).json()
        reciters = r.get("reciters", [])
        for rec in reciters:
            name = rec.get("name", "")
            if "رفعت" in name or "Rifaat" in name or "Rifat" in name or "Refaat" in name:
                for moshaf in rec.get("moshaf", []):
                    server = moshaf.get("server", "")
                    surah_list = moshaf.get("surah_list", "")
                    available = set()
                    for x in surah_list.split(","):
                        x = x.strip()
                        if x.isdigit():
                            available.add(int(x))
                    if server and available:
                        _rifaat_server = server
                        _rifaat_available = available
                        print(f"Rifaat loaded: {name} - server={server} - count={len(available)}")
                        return server, available
        print("Rifaat not found in mp3quran API")
    except Exception as e:
        print(f"Rifaat API error: {e}")
    return None, None

def get_rifaat_audio(surah_num):
    if surah_num in _rifaat_cache:
        return _rifaat_cache[surah_num]
    server, available = load_rifaat_from_api()
    if server and surah_num in available:
        url = f"{server}{surah_num:03d}.mp3"
        _rifaat_cache[surah_num] = url
        print(f"Rifaat URL for surah {surah_num}: {url}")
        return url
    print(f"Rifaat surah {surah_num} not available - server={server}")
    return None

def get_audio_url(code, surah_num):
    if code == "ar.muhammadrafat":
        url = get_rifaat_audio(surah_num)
        if url:
            return url
        return None
    return f"https://cdn.islamic.network/quran/audio-surah/128/{code}/{surah_num}.mp3"

def to_arabic_num(n):
    arabic = "٠١٢٣٤٥٦٧٨٩"
    return "".join(arabic[int(d)] for d in str(n))

def surah_keyboard():
    rows = []
    for i in range(0, len(SURAHS), 4):
        rows.append([KeyboardButton(s) for s in SURAHS[i:i+4]])
    rows.append([KeyboardButton("🏠 القائمة الرئيسية")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def rifaat_keyboard():
    rows = []
    for i in range(0, len(RIFAAT_SURAHS), 4):
        rows.append([KeyboardButton(s) for s in RIFAAT_SURAHS[i:i+4]])
    rows.append([KeyboardButton("🏠 القائمة الرئيسية")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎧 الاستماع للقرآن"), KeyboardButton("📖 قراءة السورة")],
        [KeyboardButton("🎙️ تغيير القارئ"), KeyboardButton("📿 آية اليوم")],
        [KeyboardButton("📖 تفسير السورة"), KeyboardButton("🔍 بحث باسم السورة")],
        [KeyboardButton("🔍 البحث بآية")],
        [KeyboardButton("🌅 أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
        [KeyboardButton("⏰ تذكير سورة الملك"), KeyboardButton("⏰ تذكير الواقعة")],
        [KeyboardButton("⏰ تذكير الكهف"), KeyboardButton("❌ إلغاء التذكيرات")],
    ], resize_keyboard=True)

# ================= START - عرض المميزات =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "أهلاً بيك في بوت القرآن الكريم 🤍\n"
        "━━━━━━━━━━━━━━\n"
        "📖 بوتك اليومي للقرآن والأذكار\n\n"
        "✨ مميزات البوت:\n\n"
        "🎧 الاستماع للقرآن\n"
        "اسمع أي سورة بأصوات 6 قراء\n"
        "• عبدالباسط عبدالصمد\n"
        "• مشاري العفاسي\n"
        "• الحصري\n"
        "• سعد الغامدي\n"
        "• المنشاوي\n"
        "• محمد رفعت\n\n"
        "📖 قراءة السورة\n"
        "نص السورة كامل + معلوماتها + فضلها + سبب نزولها\n\n"
        "📖 تفسير السورة\n"
        "تفسير ميسر آية آية\n\n"
        "🔍 البحث بآية\n"
        "اكتب كلمة زي الصبر - الجنة - الرحمة وهيجيبلك كل الآيات اللي فيها\n\n"
        "📿 آية اليوم\n"
        "آية عشوائية كل مرة تدوس عليها\n\n"
        "🌅 أذكار الصباح | 🌙 أذكار المساء\n"
        "أذكار كاملة\n\n"
        "⏰ تذكيرات تلقائية حسب بلدك\n"
        "• سورة الملك بعد العشاء\n"
        "• سورة الواقعة بعد الفجر\n"
        "• سورة الكهف كل جمعة\n\n"
        "━━━━━━━━━━━━━━\n"
        "👇 اختر الميزة اللي عايزها:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎧 الاستماع للقرآن", callback_data="feat:listen")],
        [InlineKeyboardButton("📖 قراءة السورة", callback_data="feat:read")],
        [InlineKeyboardButton("📖 تفسير السورة", callback_data="feat:tafsir")],
        [InlineKeyboardButton("🔍 البحث بآية", callback_data="feat:search")],
        [InlineKeyboardButton("📿 آية اليوم", callback_data="feat:ayah")],
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="feat:sabah")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="feat:masa")],
        [InlineKeyboardButton("🎙️ تغيير القارئ", callback_data="feat:reciter")],
        [InlineKeyboardButton("⏰ تذكير الملك بعد العشاء", callback_data="feat:mulk")],
        [InlineKeyboardButton("⏰ تذكير الواقعة بعد الفجر", callback_data="feat:waqia")],
        [InlineKeyboardButton("⏰ تذكير الكهف الجمعة", callback_data="feat:kahf")],
    ])
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, reply_markup=kb)
    else:
        await update.message.reply_text(text, reply_markup=kb)
        await update.message.reply_text("أو استخدم القايمة اللي تحت 👇", reply_markup=main_keyboard())

async def feature_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    feat = query.data.split(":")[1]
    user_id = query.from_user.id

    if feat == "listen" or feat == "read":
        context.user_data['mode'] = 'read'
        code_now = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        if code_now == "ar.muhammadrafat":
            await query.message.reply_text("اختر من السور المتوفرة بصوت الشيخ محمد رفعت 👇", reply_markup=rifaat_keyboard())
        else:
            await query.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
    elif feat == "tafsir":
        context.user_data['mode'] = 'tafsir'
        await query.message.reply_text("اختر السورة اللي عايز تفسيرها 👇", reply_markup=surah_keyboard())
    elif feat == "search":
        context.user_data['mode'] = 'search_ayah'
        await query.message.reply_text("🔍 ابعت الكلمة اللي عايز تدور عليها\nمثال: الصبر - الجنة - الرحمة")
    elif feat == "ayah":
        try:
            r = requests.get("https://api.alquran.cloud/v1/ayah/random/quran-uthmani").json()
            ayah = r['data']
            await query.message.reply_text(f"{ayah['text']} ﴿{to_arabic_num(ayah['numberInSurah'])}﴾\n\n— سورة {ayah['surah']['name']}")
        except:
            await query.message.reply_text("حاول تاني")
    elif feat == "sabah":
        for z in AZKAR_SABAH:
            await query.message.reply_text(z)
    elif feat == "masa":
        for z in AZKAR_MASA:
            await query.message.reply_text(z)
    elif feat == "reciter":
        kb = [[InlineKeyboardButton(name, callback_data=f"reciter:{code}")] for name, code in RECITERS.items()]
        await query.message.reply_text("اختر القارئ:", reply_markup=InlineKeyboardMarkup(kb))
    elif feat == "mulk":
        await query.message.reply_text("دوس على زرار ⏰ تذكير سورة الملك من القايمة اللي تحت 👇", reply_markup=main_keyboard())
    elif feat == "waqia":
        await query.message.reply_text("دوس على زرار ⏰ تذكير الواقعة من القايمة اللي تحت 👇", reply_markup=main_keyboard())
    elif feat == "kahf":
        await query.message.reply_text("دوس على زرار ⏰ تذكير الكهف من القايمة اللي تحت 👇", reply_markup=main_keyboard())

async def send_surah_text(context, chat_id, surah_num, surah_name, intro_text, audio_caption):
    try:
        await context.bot.send_message(chat_id=chat_id, text=intro_text)
        data = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_num}/quran-uthmani").json()['data']
        full = ""
        for a in data['ayahs']:
            full += f"{a['text']} ﴿{to_arabic_num(a['numberInSurah'])}﴾ "
        header = f"✦ ━━━━ سورة {surah_name} ━━━━ ✦\n\nبِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ\n\n"
        footer = "\n\n━━━ صدق الله العظيم ━━━"
        text = header + full + footer
        for i in range(0, len(text), 3800):
            await context.bot.send_message(chat_id=chat_id, text=text[i:i+3800])
        await context.bot.send_audio(chat_id=chat_id, audio=f"https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/{surah_num}.mp3", title=surah_name, performer="عبدالباسط عبدالصمد", caption=audio_caption)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"وقت سورة {surah_name} 🤍\nافتحها من هنا: https://quran.com/{surah_num}")

async def send_mulk_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_surah_text(context, context.job.chat_id, 67, "الملك",
        "⏰ وقتك مع سورة الملك بعد العشاء 🤍\n\nمن قرأها كل ليلة منجية من عذاب القبر، يلا نقرأها سوا قبل النوم:",
        "🎧 سورة الملك - تذكير بعد العشاء")

async def send_waqia_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_surah_text(context, context.job.chat_id, 56, "الواقعة",
        "🕌 وقتك مع سورة الواقعة بعد الفجر 🤍\n\nمن قرأها كل ليلة لم تصبه فاقة أبدا، وهي سورة الغنى والرزق\nيلا نقرأها سوا بعد صلاة الفجر:",
        "🎧 سورة الواقعة - تذكير بعد الفجر")

async def send_kahf_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_surah_text(context, context.job.chat_id, 18, "الكهف",
        "🕌 جمعة مباركة 🤍\n\nمن قرأ سورة الكهف يوم الجمعة أضاء له من النور ما بين الجمعتين\nيلا نقرأها سوا:",
        "🎧 سورة الكهف - تذكير الجمعة")

def get_prayer_times(city):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5"
        r = requests.get(url, timeout=10).json()
        timings = r['data']['timings']
        def add_minutes(time_str, add):
            h, m = map(int, time_str.split(":"))
            m += add
            if m >= 60:
                h += 1
                m -= 60
            if h >= 24:
                h -= 24
            return h, m
        fajr = add_minutes(timings['Fajr'], 15)
        isha = add_minutes(timings['Isha'], 15)
        return fajr, isha
    except Exception as e:
        print(f"Prayer error: {e}")
        return (5, 30), (20, 30)

def get_fajr_time(city):
    fajr, _ = get_prayer_times(city)
    return fajr

def get_isha_time(city):
    _, isha = get_prayer_times(city)
    return isha

async def schedule_waqia_after_fajr(context, chat_id, user_id, city):
    import datetime
    for j in context.job_queue.get_jobs_by_name(f"waqia_{chat_id}"):
        j.schedule_removal()
    hour, minute = get_fajr_time(city)
    context.job_queue.run_daily(send_waqia_reminder, time=datetime.time(hour=hour, minute=minute), chat_id=chat_id, name=f"waqia_{chat_id}")
    return hour, minute

async def schedule_mulk_after_isha(context, chat_id, user_id, city):
    import datetime
    for j in context.job_queue.get_jobs_by_name(f"mulk_{chat_id}"):
        j.schedule_removal()
    hour, minute = get_isha_time(city)
    context.job_queue.run_daily(send_mulk_reminder, time=datetime.time(hour=hour, minute=minute), chat_id=chat_id, name=f"mulk_{chat_id}")
    return hour, minute

async def ensure_daily_update_job(context, chat_id):
    import datetime
    exists = context.job_queue.get_jobs_by_name(f"prayer_update_{chat_id}")
    if not exists:
        context.job_queue.run_daily(update_prayer_jobs, time=datetime.time(hour=0, minute=5), chat_id=chat_id, name=f"prayer_update_{chat_id}")

async def update_prayer_jobs(context: ContextTypes.DEFAULT_TYPE):
    import datetime
    chat_id = context.job.chat_id
    city = user_city.get(chat_id, "Cairo")
    if context.job_queue.get_jobs_by_name(f"waqia_{chat_id}"):
        for j in context.job_queue.get_jobs_by_name(f"waqia_{chat_id}"):
            j.schedule_removal()
        h, m = get_fajr_time(city)
        context.job_queue.run_daily(send_waqia_reminder, time=datetime.time(hour=h, minute=m), chat_id=chat_id, name=f"waqia_{chat_id}")
    if context.job_queue.get_jobs_by_name(f"mulk_{chat_id}"):
        for j in context.job_queue.get_jobs_by_name(f"mulk_{chat_id}"):
            j.schedule_removal()
        h, m = get_isha_time(city)
        context.job_queue.run_daily(send_mulk_reminder, time=datetime.time(hour=h, minute=m), chat_id=chat_id, name=f"mulk_{chat_id}")

async def do_search_ayah(keyword, update):
    if len(keyword) < 2:
        await update.message.reply_text("❌ اكتب كلمة أطول من حرف، مثال: الصبر - الجنة - الرحمة")
        return
    msg = await update.message.reply_text(f"🔍 جاري البحث عن `{keyword}` ...")
    try:
        url = f"https://api.alquran.cloud/v1/search/{keyword}/all/quran-uthmani"
        r = requests.get(url, timeout=15).json()
        if r["code"] != 200 or r["data"]["count"] == 0:
            await msg.edit_text(f"❌ ملقتش أي آية فيها كلمة `{keyword}`\nجرب كلمة تانية")
            return
        count = r["data"]["count"]
        matches = r["data"]["matches"][:5]
        text = f"🔍 لقيت {count} آية فيها `{keyword}`\n\n"
        for i, m in enumerate(matches, 1):
            ayah_text = m["text"]
            surah_name = m["surah"]["name"]
            ayah_num = m["numberInSurah"]
            text += f"{i}️⃣ {ayah_text} ﴿{to_arabic_num(ayah_num)}﴾\n— سورة {surah_name}\n\n"
        text += "عشان تكمل البحث ابعت كلمة تانية 👇\nأو دوس 🏠 القائمة الرئيسية"
        await msg.edit_text(text)
    except Exception as e:
        print(f"Search error: {e}")
        await msg.edit_text("❌ حصل خطأ في البحث، جرب تاني")

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
        code_now = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        if code_now == "ar.muhammadrafat":
            await update.message.reply_text("اختر من السور المتوفرة بصوت الشيخ محمد رفعت 👇", reply_markup=rifaat_keyboard())
        else:
            await update.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

    if text == "🔍 البحث بآية":
        context.user_data['mode'] = 'search_ayah'
        await update.message.reply_text(
            "🔍 البحث بآية\n\n"
            "ابعت الكلمة اللي عايز تدور عليها 👇\n"
            "مثال: الصبر - الجنة - الرحمة - الصلاة\n\n"
            "اكتب الكلمة وابعتها دلوقتي",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True)
        )
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
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_mulk_after_isha(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(
                f"✅ تم تفعيل تذكير سورة الملك!\n\n"
                f"📍 مدينتك: {city}\n"
                f"🕌 هيبعتلك بعد العشاء بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})\n\n"
                f"كل يوم بعد العشاء هبعتلك سورة الملك كاملة نص + صوت 🤍",
                reply_markup=main_keyboard()
            )
        else:
            context.user_data['mode'] = 'ask_city_mulk'
            await update.message.reply_text(
                "⏰ تذكير سورة الملك بعد العشاء 🤍\n\n"
                "عشان البوت يبعتلك بعد العشاء بتوقيت بلدك بالظبط، ابعت اسم مدينتك 👇\n\n"
                "مثال: سوهاج - القاهرة - الرياض - جدة - بغداد - الجزائر\n\n"
                "اكتب اسم مدينتك وابعتها",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True)
            )
        return

    if text == "⏰ تذكير الواقعة":
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_waqia_after_fajr(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(
                f"✅ تم تفعيل تذكير سورة الواقعة!\n\n"
                f"📍 مدينتك: {city}\n"
                f"🕌 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})\n\n"
                f"كل يوم بعد الفجر هبعتلك سورة الواقعة كاملة نص + صوت 🤍",
                reply_markup=main_keyboard()
            )
        else:
            context.user_data['mode'] = 'ask_city_waqia'
            await update.message.reply_text(
                "⏰ تذكير سورة الواقعة بعد الفجر 🤍\n\n"
                "عشان البوت يبعتلك بعد الفجر بتوقيت بلدك بالظبط، ابعت اسم مدينتك 👇\n\n"
                "مثال: سوهاج - القاهرة - الرياض - جدة - بغداد - الجزائر\n\n"
                "اكتب اسم مدينتك وابعتها",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True)
            )
        return

    if text == "⏰ تذكير الكهف":
        try:
            import datetime
            for j in context.job_queue.get_jobs_by_name(f"kahf_{chat_id}"):
                j.schedule_removal()
            context.job_queue.run_daily(send_kahf_reminder, time=datetime.time(hour=10, minute=0), days=(4,), chat_id=chat_id, name=f"kahf_{chat_id}")
            await update.message.reply_text("✅ تم تفعيل تذكير سورة الكهف!\n\nكل يوم جمعة الساعة 10 صباحا هبعتلك سورة الكهف كاملة نص + صوت 🕌\n\nمن قرأها يوم الجمعة أضاء له من النور ما بين الجمعتين")
        except:
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

    if text == "❌ إلغاء التذكيرات":
        try:
            for name in [f"mulk_{chat_id}", f"waqia_{chat_id}", f"kahf_{chat_id}", f"prayer_update_{chat_id}"]:
                for j in context.job_queue.get_jobs_by_name(name):
                    j.schedule_removal()
            await update.message.reply_text("تم إلغاء كل التذكيرات ❌\n(الملك - الواقعة - الكهف)")
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

    if context.user_data.get('mode') == 'ask_city_mulk':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد العشاء في {city} ...")
        hour, minute = await schedule_mulk_after_isha(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(
            f"✅ تم تفعيل تذكير سورة الملك!\n\n"
            f"📍 مدينتك: {city}\n"
            f"🕌 هيبعتلك بعد العشاء بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})\n\n"
            f"كل يوم بعد العشاء هبعتلك سورة الملك كاملة نص + صوت 🤍\n"
            f"وكل يوم البوت هيحدث المعاد تلقائي",
            reply_markup=main_keyboard()
        )
        return

    if context.user_data.get('mode') == 'ask_city_waqia':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد الفجر في {city} ...")
        hour, minute = await schedule_waqia_after_fajr(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(
            f"✅ تم تفعيل تذكير سورة الواقعة!\n\n"
            f"📍 مدينتك: {city}\n"
            f"🕌 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})\n\n"
            f"كل يوم بعد الفجر هبعتلك سورة الواقعة كاملة نص + صوت 🤍\n"
            f"وكل يوم البوت هيحدث المعاد تلقائي لأن الفجر بيتحرك كل يوم",
            reply_markup=main_keyboard()
        )
        return

    if context.user_data.get('mode') == 'search_ayah':
        await do_search_ayah(text, update)
        return

    if text in SURAHS:
        n = SURAHS.index(text) + 1
        mode = context.user_data.get('mode', 'read')
        code = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        reciter_name = "عبدالباسط عبدالصمد"
        for k, v in RECITERS.items():
            if v == code:
                reciter_name = k

        if code == "ar.muhammadrafat" and text not in RIFAAT_SURAHS:
            await update.message.reply_text(
                f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت\n\n"
                f"الشيخ رفعت ليه سور معينة بس، زي بوت IslamicQuranBot بالظبط.\n"
                f"اختر سورة من القايمة دي 👇",
                reply_markup=rifaat_keyboard()
            )
            return

        if mode == 'tafsir':
            await update.message.reply_text(f"جاري تحميل تفسير سورة {text} 📖 ...")
            try:
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

        audio_url = get_audio_url(code, n)
        if code == "ar.muhammadrafat" and audio_url is None:
            await update.message.reply_text(
                f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت في السيرفرات حاليا\n"
                f"جرب سورة تانية من القايمة، أو اسمعها بصوت عبدالباسط 👇"
            )
            try:
                await update.message.reply_audio(
                    audio=f"https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/{n}.mp3",
                    title=text,
                    performer="عبدالباسط عبدالصمد",
                    caption=f"🎧 سورة {text} - عبدالباسط عبدالصمد"
                )
            except:
                pass
        else:
            try:
                await update.message.reply_audio(
                    audio=audio_url,
                    title=text,
                    performer=reciter_name,
                    caption=f"🎧 سورة {text} - {reciter_name}"
                )
            except Exception as e:
                print(f"Audio error {reciter_name} surah {n}: {e} - URL was: {audio_url}")
                if code == "ar.muhammadrafat":
                    await update.message.reply_text(
                        f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت في السيرفرات حاليا\n"
                        f"جرب سورة تانية من القايمة، أو اسمعها بصوت عبدالباسط 👇"
                    )
                    try:
                        await update.message.reply_audio(
                            audio=f"https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/{n}.mp3",
                            title=text,
                            performer="عبدالباسط عبدالصمد",
                            caption=f"🎧 سورة {text} - عبدالباسط عبدالصمد"
                        )
                    except:
                        pass
                else:
                    await update.message.reply_text("⚠️ الصوت مش متوفر دلوقتي، النص اتبعت كامل فوق 👆")
        try:
            await msg.delete()
        except:
            pass
        return

    await update.message.reply_text("اكتب اسم سورة صحيح أو اختر من القائمة 👇", reply_markup=surah_keyboard())

async def reciter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.split(":")[1]
    user_reciter[query.from_user.id] = code
    name = [k for k,v in RECITERS.items() if v==code][0]
    await query.edit_message_text(f"تم اختيار القارئ: {name} ✅\nالآن اختر السورة:")
    if code == "ar.muhammadrafat":
        await query.message.reply_text(
            "⚠️ تنبيه: الشيخ محمد رفعت ليه سور معينة بس مسجلة، مش المصحف كله\nاختر من السور المتوفرة 👇",
            reply_markup=rifaat_keyboard()
        )
    else:
        await query.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reciter_callback, pattern="^reciter:"))
    app.add_handler(CallbackQueryHandler(feature_callback, pattern="^feat:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot is running...")
    app.run_polling()
