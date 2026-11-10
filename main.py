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

# ============ المشايخ + أنواع التلاوة - جديد ============
SHEIKHS = {
    "عبدالباسط عبدالصمد": {
        "مرتل": "ar.abdulbasitmurattal",
        "مجود": "abdulbasit_mujawwad",
        "تلاوات نادرة": "abdulbasit_rare",
    },
    "مشاري راشد العفاسي": {
        "مرتل": "ar.alafasy",
    },
    "محمود خليل الحصري": {
        "مرتل": "ar.husary",
        "مجود": "husary_mujawwad",
    },
    "سعد الغامدي": {
        "مرتل": "ar.aymanswoaid",
    },
    "محمد المنشاوي": {
        "مرتل": "ar.minshawi",
        "مجود": "minshawi_mujawwad",
    },
    "محمد رفعت": {
        "مرتل": "ar.muhammadrafat",
    },
}

# عشان الكود القديم يفضل شغال
RECITERS = {}
for _sheikh, _styles in SHEIKHS.items():
    for _style, _code in _styles.items():
        RECITERS[f"{_sheikh} - {_style}"] = _code

# سيرفرات المجود من mp3quran
MUJAWWAD_SERVERS = {
    "abdulbasit_mujawwad": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/",
    "husary_mujawwad": "https://server13.mp3quran.net/husr/Almusshaf-Al-Mojawwad/",
    "minshawi_mujawwad": "https://server10.mp3quran.net/minsh/Almusshaf-Al-Mojawwad/",
}

# تلاوات نادرة - عبدالباسط
RARE_TILAWAT = {
    "💎 مريم - تلاوة نادرة 1968": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/019.mp3",
    "💎 يوسف - تلاوة نادرة": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/012.mp3",
    "💎 الكهف - الحرم المكي": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/018.mp3",
    "💎 يس - مجود نادر": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/036.mp3",
    "💎 الحاقة - مجود": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/069.mp3",
    "💎 الفجر - مجود": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/089.mp3",
    "💎 التكوير - مجود نادر": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/081.mp3",
    "💎 القمر - مجود": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/054.mp3",
    "💎 الرحمن - مجود": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/055.mp3",
    "💎 الواقعة - مجود": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/056.mp3",
    "💎 النازعات - مجود نادر": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/079.mp3",
    "💎 عبس - مجود نادر": "https://server7.mp3quran.net/basit/Almusshaf-Al-Mojawwad/080.mp3",
}

def get_mujawwad_url(code, surah_num):
    server = MUJAWWAD_SERVERS.get(code)
    if server:
        return f"{server}{surah_num:03d}.mp3"
    return None

def sheikhs_keyboard():
    kb = []
    for sheikh in SHEIKHS.keys():
        kb.append([InlineKeyboardButton(f"🎙️ {sheikh}", callback_data=f"sheikh:{sheikh}")])
    return InlineKeyboardMarkup(kb)

def styles_keyboard(sheikh):
    styles = SHEIKHS.get(sheikh, {})
    kb = []
    for style in styles.keys():
        if style == "مرتل":
            emoji = "🎧"
        elif style == "مجود":
            emoji = "✨"
        else:
            emoji = "💎"
        kb.append([InlineKeyboardButton(f"{emoji} {style}", callback_data=f"style:{sheikh}:{style}")])
    kb.append([InlineKeyboardButton("⬅️ رجوع للمشايخ", callback_data="back_sheikhs")])
    return InlineKeyboardMarkup(kb)

def rare_keyboard():
    rows = []
    keys = list(RARE_TILAWAT.keys())
    for i in range(0, len(keys), 2):
        rows.append([KeyboardButton(k) for k in keys[i:i+2]])
    rows.append([KeyboardButton("🏠 القائمة الرئيسية")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

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

RADIO_WEB_URL = "https://misrquran.gov.eg/home"

user_reciter = {}
user_city = {}
user_coords = {}

# ================= الشيخ محمد رفعت =================
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
                        return server, available
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
        return url
    return None

def get_audio_url(code, surah_num):
    if code == "ar.muhammadrafat":
        url = get_rifaat_audio(surah_num)
        if url:
            return url
        return None
    if code in MUJAWWAD_SERVERS:
        return get_mujawwad_url(code, surah_num)
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
        [KeyboardButton("📻 راديو القرآن الكريم - مصر")],
        [KeyboardButton("📖 تفسير السورة"), KeyboardButton("🔍 بحث باسم السورة")],
        [KeyboardButton("🔍 البحث بآية")],
        [KeyboardButton("🌅 أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
        [KeyboardButton("📅 التقويم والمواقيت"), KeyboardButton("🕌 مواقيت الصلاة")],
        [KeyboardButton("📍 ابعت موقعك للمواقيت"), KeyboardButton("🏙️ تغيير مدينتي")],
        [KeyboardButton("✨ عبدالباسط - مجود"), KeyboardButton("💎 تلاوات نادرة")],
        [KeyboardButton("⏰ تذكير أذكار الصباح"), KeyboardButton("⏰ تذكير أذكار المساء")],
        [KeyboardButton("⏰ تذكير سورة الملك"), KeyboardButton("⏰ تذكير الواقعة")],
        [KeyboardButton("⏰ تذكير الكهف"), KeyboardButton("❌ إلغاء التذكيرات")],
    ], resize_keyboard=True)

# ================= التقويم + مواقيت الصلاة =================
def clean_prayer_time(t):
    return t.split(" ")[0]

def get_calendar_data(user_id):
    if user_id in user_coords:
        lat = user_coords[user_id]["lat"]
        lon = user_coords[user_id]["lon"]
        url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=5"
        city_label = "موقعك 📍"
    elif user_id in user_city:
        city = user_city[user_id]
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5"
        city_label = city
    else:
        url = "https://api.aladhan.com/v1/timingsByCity?city=Sohag&country=Egypt&method=5"
        city_label = "سوهاج (افتراضي)"
    r = requests.get(url, timeout=15).json()
    return r["data"], city_label

def format_calendar_message(data, city_label):
    timings = data["timings"]
    greg = data["date"]["gregorian"]
    hijri = data["date"]["hijri"]
    weekday_ar_map = {"Monday":"الاثنين","Tuesday":"الثلاثاء","Wednesday":"الأربعاء","Thursday":"الخميس","Friday":"الجمعة","Saturday":"السبت","Sunday":"الأحد"}
    month_ar_map = {"January":"يناير","February":"فبراير","March":"مارس","April":"أبريل","May":"مايو","June":"يونيو","July":"يوليو","August":"أغسطس","September":"سبتمبر","October":"أكتوبر","November":"نوفمبر","December":"ديسمبر"}
    weekday_ar = weekday_ar_map.get(greg["weekday"]["en"], greg["weekday"]["en"])
    month_ar = month_ar_map.get(greg["month"]["en"], greg["month"]["en"])
    return f"""📅 التقويم
━━━━━━━━━━━━━━
🗓️ اليوم: {weekday_ar}
🗓️ ميلادي: {greg['day']} {month_ar} {greg['year']} م
🌙 هجري: {hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ
📍 المكان: {city_label}

🕌 مواقيت الصلاة
━━━━━━━━━━━━━━
🌅 الفجر: {clean_prayer_time(timings['Fajr'])}
🌞 الشروق: {clean_prayer_time(timings['Sunrise'])}
☀️ الظهر: {clean_prayer_time(timings['Dhuhr'])}
🌤️ العصر: {clean_prayer_time(timings['Asr'])}
🌇 المغرب: {clean_prayer_time(timings['Maghrib'])}
🌙 العشاء: {clean_prayer_time(timings['Isha'])}
🕛 منتصف الليل: {clean_prayer_time(timings['Midnight'])}
"""

def get_next_prayer_text(data):
    from datetime import datetime
    timings = data["timings"]
    now = datetime.now().strftime("%H:%M")
    order = [("الفجر","Fajr"),("الشروق","Sunrise"),("الظهر","Dhuhr"),("العصر","Asr"),("المغرب","Maghrib"),("العشاء","Isha")]
    for name, key in order:
        t = clean_prayer_time(timings[key])
        if t > now:
            h1, m1 = map(int, now.split(":"))
            h2, m2 = map(int, t.split(":"))
            diff = (h2*60+m2) - (h1*60+m1)
            hh, mm = divmod(diff, 60)
            return f"⏰ الصلاة الجاية: {name}\n🕐 الساعة: {t}\n⏳ باقي عليها: {hh} ساعة و {mm} دقيقة"
    return f"⏰ الصلاة الجاية: الفجر بكرة\n🕐 الساعة: {clean_prayer_time(timings['Fajr'])}"

async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data, city_label = get_calendar_data(update.effective_user.id)
        await update.message.reply_text(format_calendar_message(data, city_label), reply_markup=main_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ حصل خطأ: {e}")

async def prayer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data, city_label = get_calendar_data(update.effective_user.id)
        await update.message.reply_text(f"🕌 مواقيت الصلاة - {city_label}\n━━━━━━━━━━━━━━\n\n{get_next_prayer_text(data)}", reply_markup=main_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ حصل خطأ: {e}")

async def setcity_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب كده: /setcity سوهاج")
        return
    city = " ".join(context.args)
    user_city[update.effective_user.id] = city
    if update.effective_user.id in user_coords:
        del user_coords[update.effective_user.id]
    await update.message.reply_text(f"✅ تم ضبط المدينة على: {city}\nجرب /today", reply_markup=main_keyboard())

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    user_coords[update.effective_user.id] = {"lat": loc.latitude, "lon": loc.longitude}
    await update.message.reply_text("✅ تم حفظ موقعك!\nدلوقتي المواقيت حسب مكانك بالظبط.\nجرب 📅 التقويم والمواقيت", reply_markup=main_keyboard())

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "أهلاً بيك في بوت القرآن الكريم 🤍\n"
        "━━━━━━━━━━━━━━\n"
        "📖 بوتك اليومي للقرآن والأذكار\n\n"
        "✨ مميزات البوت:\n\n"
        "🎧 الاستماع للقرآن\n"
        "اسمع أي سورة بأصوات المشايخ\n"
        "• عبدالباسط - مرتل / مجود / تلاوات نادرة\n"
        "• مشاري العفاسي\n"
        "• الحصري - مرتل / مجود\n"
        "• سعد الغامدي\n"
        "• المنشاوي - مرتل / مجود\n"
        "• محمد رفعت\n\n"
        "📻 راديو القرآن الكريم - مصر\n"
        "بث مباشر 24 ساعة من القاهرة\n\n"
        "📖 قراءة السورة + تفسير + بحث بآية\n\n"
        "📅 التقويم والمواقيت 🆕\n"
        "ميلادي + هجري + مواقيت الصلاة حسب مكانك\n\n"
        "🌅 أذكار الصباح | 🌙 أذكار المساء\n"
        "⏰ تذكيرات: أذكار الصباح - أذكار المساء - الملك - الواقعة - الكهف\n\n"
        "━━━━━━━━━━━━━━\n"
        "👇 اختر الميزة اللي عايزها:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎧 الاستماع للقرآن", callback_data="feat:listen")],
        [InlineKeyboardButton("📻 راديو القرآن الكريم - مصر", callback_data="feat:radio_menu")],
        [InlineKeyboardButton("📖 قراءة السورة", callback_data="feat:read")],
        [InlineKeyboardButton("📖 تفسير السورة", callback_data="feat:tafsir")],
        [InlineKeyboardButton("🔍 البحث بآية", callback_data="feat:search")],
        [InlineKeyboardButton("📿 آية اليوم", callback_data="feat:ayah")],
        [InlineKeyboardButton("📅 التقويم والمواقيت", callback_data="feat:calendar")],
        [InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="feat:prayer")],
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="feat:sabah")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="feat:masa")],
        [InlineKeyboardButton("🎙️ تغيير القارئ", callback_data="feat:reciter")],
        [InlineKeyboardButton("⏰ تذكير أذكار الصباح", callback_data="feat:sabah_rem")],
        [InlineKeyboardButton("⏰ تذكير أذكار المساء", callback_data="feat:masa_rem")],
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

async def send_radio_menu(msg_obj):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ افتح الراديو - الموقع الرسمي", url=RADIO_WEB_URL)],
        [InlineKeyboardButton("▶️ اسمع من يوتيوب - بث مباشر", url="https://www.youtube.com/results?search_query=%D8%A5%D8%B0%D8%A7%D8%B9%D8%A9+%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86+%D8%A7%D9%84%D9%83%D8%B1%D9%8A%D9%85+%D9%85%D9%86+%D8%A7%D9%84%D9%82%D8%A7%D9%87%D8%B1%D8%A9+%D8%A8%D8%AB+%D9%85%D8%A8%D8%A7%D8%B4%D8%B1")],
        [InlineKeyboardButton("▶️ اسمع من راديو جاردن - شغال دايما", url="https://radio.garden/listen/quran-radio-cairo/")],
    ])
    await msg_obj.reply_text(
        "📻 إذاعة القرآن الكريم من القاهرة\n"
        "━━━━━━━━━━━━━━\n"
        "بث مباشر 24 ساعة\n"
        "عبدالباسط - الحُصري - المنشاوي - مصطفى إسماعيل - محمد رفعت\n\n"
        "دوس على أي زرار، هيفتح الراديو في المتصفح 👇",
        reply_markup=kb
    )

async def feature_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    feat = query.data.split(":")[1]
    user_id = query.from_user.id
    if feat == "radio_menu":
        await send_radio_menu(query.message)
        return
    elif feat == "calendar":
        try:
            data, city_label = get_calendar_data(user_id)
            await query.message.reply_text(format_calendar_message(data, city_label))
        except Exception as e:
            await query.message.reply_text(f"❌ حصل خطأ: {e}")
        return
    elif feat == "prayer":
        try:
            data, city_label = get_calendar_data(user_id)
            await query.message.reply_text(f"🕌 مواقيت الصلاة - {city_label}\n━━━━━━━━━━━━━━\n\n{get_next_prayer_text(data)}")
        except Exception as e:
            await query.message.reply_text(f"❌ حصل خطأ: {e}")
        return
    elif feat == "listen" or feat == "read":
        context.user_data['mode'] = 'read'
        code_now = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        if code_now == "ar.muhammadrafat":
            await query.message.reply_text("اختر من السور المتوفرة بصوت الشيخ محمد رفعت 👇", reply_markup=rifaat_keyboard())
        elif code_now == "abdulbasit_rare":
            await query.message.reply_text("اختر التلاوة النادرة 👇", reply_markup=rare_keyboard())
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
    elif feat == "sabah_rem":
        await query.message.reply_text("دوس على زرار ⏰ تذكير أذكار الصباح من القايمة اللي تحت 👇", reply_markup=main_keyboard())
    elif feat == "masa_rem":
        await query.message.reply_text("دوس على زرار ⏰ تذكير أذكار المساء من القايمة اللي تحت 👇", reply_markup=main_keyboard())
    elif feat == "reciter":
        await query.message.reply_text("🎙️ اختر الشيخ:", reply_markup=sheikhs_keyboard())
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
    await send_surah_text(context, context.job.chat_id, 67, "الملك", "⏰ وقتك مع سورة الملك بعد العشاء 🤍\n\nمن قرأها كل ليلة منجية من عذاب القبر:", "🎧 سورة الملك - تذكير بعد العشاء")

async def send_waqia_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_surah_text(context, context.job.chat_id, 56, "الواقعة", "🕌 وقتك مع سورة الواقعة بعد الفجر 🤍\n\nمن قرأها كل ليلة لم تصبه فاقة أبدا:", "🎧 سورة الواقعة - تذكير بعد الفجر")

async def send_kahf_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_surah_text(context, context.job.chat_id, 18, "الكهف", "🕌 جمعة مباركة 🤍\n\nمن قرأ سورة الكهف يوم الجمعة أضاء له من النور ما بين الجمعتين:", "🎧 سورة الكهف - تذكير الجمعة")

async def send_sabah_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="🌅 وقت أذكار الصباح 🤍\n\nأصبحنا وأصبح الملك لله:")
    for z in AZKAR_SABAH:
        await context.bot.send_message(chat_id=chat_id, text=z)
    await context.bot.send_message(chat_id=chat_id, text="━━━ تقبل الله منا ومنكم صباحكم ذكر 🤍 ━━━", reply_markup=main_keyboard())

async def send_masa_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="🌙 وقت أذكار المساء 🤍\n\nأمسينا وأمسى الملك لله:")
    for z in AZKAR_MASA:
        await context.bot.send_message(chat_id=chat_id, text=z)
    await context.bot.send_message(chat_id=chat_id, text="━━━ تقبل الله منا ومنكم مساءكم ذكر 🤍 ━━━", reply_markup=main_keyboard())

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
        return add_minutes(timings['Fajr'], 15), add_minutes(timings['Asr'], 15), add_minutes(timings['Isha'], 15)
    except Exception as e:
        print(f"Prayer error: {e}")
        return (5, 30), (15, 30), (20, 30)

def get_fajr_time(city):
    fajr, _, _ = get_prayer_times(city)
    return fajr
def get_asr_time(city):
    _, asr, _ = get_prayer_times(city)
    return asr
def get_isha_time(city):
    _, _, isha = get_prayer_times(city)
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

async def schedule_sabah_after_fajr(context, chat_id, user_id, city):
    import datetime
    for j in context.job_queue.get_jobs_by_name(f"sabah_{chat_id}"):
        j.schedule_removal()
    hour, minute = get_fajr_time(city)
    context.job_queue.run_daily(send_sabah_reminder, time=datetime.time(hour=hour, minute=minute), chat_id=chat_id, name=f"sabah_{chat_id}")
    return hour, minute

async def schedule_masa_after_asr(context, chat_id, user_id, city):
    import datetime
    for j in context.job_queue.get_jobs_by_name(f"masa_{chat_id}"):
        j.schedule_removal()
    hour, minute = get_asr_time(city)
    context.job_queue.run_daily(send_masa_reminder, time=datetime.time(hour=hour, minute=minute), chat_id=chat_id, name=f"masa_{chat_id}")
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
    if context.job_queue.get_jobs_by_name(f"sabah_{chat_id}"):
        for j in context.job_queue.get_jobs_by_name(f"sabah_{chat_id}"):
            j.schedule_removal()
        h, m = get_fajr_time(city)
        context.job_queue.run_daily(send_sabah_reminder, time=datetime.time(hour=h, minute=m), chat_id=chat_id, name=f"sabah_{chat_id}")
    if context.job_queue.get_jobs_by_name(f"masa_{chat_id}"):
        for j in context.job_queue.get_jobs_by_name(f"masa_{chat_id}"):
            j.schedule_removal()
        h, m = get_asr_time(city)
        context.job_queue.run_daily(send_masa_reminder, time=datetime.time(hour=h, minute=m), chat_id=chat_id, name=f"masa_{chat_id}")

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
            text += f"{i}️⃣ {m['text']} ﴿{to_arabic_num(m['numberInSurah'])}﴾\n— سورة {m['surah']['name']}\n\n"
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

    if text == "📅 التقويم والمواقيت":
        try:
            data, city_label = get_calendar_data(user_id)
            await update.message.reply_text(format_calendar_message(data, city_label))
        except Exception as e:
            await update.message.reply_text(f"❌ حصل خطأ: {e}")
        return

    if text == "🕌 مواقيت الصلاة":
        try:
            data, city_label = get_calendar_data(user_id)
            await update.message.reply_text(f"🕌 مواقيت الصلاة - {city_label}\n━━━━━━━━━━━━━━\n\n{get_next_prayer_text(data)}\n\nللمواقيت كاملة دوس 📅 التقويم والمواقيت")
        except Exception as e:
            await update.message.reply_text(f"❌ حصل خطأ: {e}")
        return

    if text == "📍 ابعت موقعك للمواقيت":
        await update.message.reply_text("📍 ابعت موقعك عشان المواقيت تبقى مظبوطة 100%\n\nدوس على 📎 تحت > Location > Send My Current Location\n\nأو دوس 🏙️ تغيير مدينتي واكتب اسم مدينتك", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "🏙️ تغيير مدينتي":
        context.user_data['mode'] = 'ask_city_calendar'
        await update.message.reply_text("🏙️ تغيير مدينتي\n\nاكتب اسم مدينتك 👇\nمثال: سوهاج - القاهرة - الرياض", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if context.user_data.get('mode') == 'ask_city_calendar':
        city = text.strip()
        user_city[user_id] = city
        if user_id in user_coords:
            del user_coords[user_id]
        context.user_data['mode'] = None
        await update.message.reply_text(f"✅ تم ضبط المدينة على: {city}\nجاري جلب التقويم...")
        try:
            data, city_label = get_calendar_data(user_id)
            await update.message.reply_text(format_calendar_message(data, city_label), reply_markup=main_keyboard())
        except:
            await update.message.reply_text(f"✅ تم حفظ {city}", reply_markup=main_keyboard())
        return

    if text == "📻 راديو القرآن الكريم - مصر":
        await send_radio_menu(update.message)
        return

    # ===== عبدالباسط مجود - زرار مباشر =====
    if text == "✨ عبدالباسط - مجود":
        user_reciter[user_id] = "abdulbasit_mujawwad"
        context.user_data['mode'] = 'read'
        await update.message.reply_text("✨ المصحف المجود - عبدالباسط عبدالصمد 🤍\n\nاختر السورة 👇", reply_markup=surah_keyboard())
        return

    if text == "💎 تلاوات نادرة":
        user_reciter[user_id] = "abdulbasit_rare"
        await update.message.reply_text("💎 تلاوات نادرة - عبدالباسط عبدالصمد\n\nاختر التلاوة 👇", reply_markup=rare_keyboard())
        return

    if text in RARE_TILAWAT:
        url = RARE_TILAWAT[text]
        await update.message.reply_text(f"جاري تحميل {text} ...")
        try:
            await update.message.reply_audio(audio=url, title=text, performer="عبدالباسط عبدالصمد - تلاوة نادرة", caption=f"💎 {text}\nعبدالباسط عبدالصمد - تلاوة نادرة 🤍")
        except:
            await update.message.reply_text(f"اسمعها من هنا:\n{url}")
        return

    if text in ["🎧 الاستماع للقرآن", "📖 قراءة السورة", "🔍 بحث باسم السورة"]:
        context.user_data['mode'] = 'read'
        code_now = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        if code_now == "ar.muhammadrafat":
            await update.message.reply_text("اختر من السور المتوفرة بصوت الشيخ محمد رفعت 👇", reply_markup=rifaat_keyboard())
        elif code_now == "abdulbasit_rare":
            await update.message.reply_text("اختر التلاوة النادرة 👇", reply_markup=rare_keyboard())
        else:
            await update.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

    if text == "🔍 البحث بآية":
        context.user_data['mode'] = 'search_ayah'
        await update.message.reply_text("🔍 البحث بآية\n\nابعت الكلمة اللي عايز تدور عليها 👇\nمثال: الصبر - الجنة - الرحمة", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "📖 تفسير السورة":
        context.user_data['mode'] = 'tafsir'
        await update.message.reply_text("اختر السورة اللي عايز تفسيرها 👇", reply_markup=surah_keyboard())
        return

    if text == "🎙️ تغيير القارئ":
        await update.message.reply_text("🎙️ اختر الشيخ:", reply_markup=sheikhs_keyboard())
        return

    if text == "🌅 أذكار الصباح":
        for z in AZKAR_SABAH:
            await update.message.reply_text(z)
        return

    if text == "🌙 أذكار المساء":
        for z in AZKAR_MASA:
            await update.message.reply_text(z)
        return

    if text == "⏰ تذكير أذكار الصباح":
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_sabah_after_fajr(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(f"✅ تم تفعيل تذكير أذكار الصباح!\n\n📍 مدينتك: {city}\n🌅 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        else:
            context.user_data['mode'] = 'ask_city_sabah'
            await update.message.reply_text("⏰ تذكير أذكار الصباح 🤍\n\nابعت اسم مدينتك 👇\nمثال: سوهاج - القاهرة - الرياض", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "⏰ تذكير أذكار المساء":
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_masa_after_asr(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(f"✅ تم تفعيل تذكير أذكار المساء!\n\n📍 مدينتك: {city}\n🌙 هيبعتلك بعد العصر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        else:
            context.user_data['mode'] = 'ask_city_masa'
            await update.message.reply_text("⏰ تذكير أذكار المساء 🤍\n\nابعت اسم مدينتك 👇", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "⏰ تذكير سورة الملك":
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_mulk_after_isha(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(f"✅ تم تفعيل تذكير سورة الملك!\n\n📍 مدينتك: {city}\n🕌 هيبعتلك بعد العشاء بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        else:
            context.user_data['mode'] = 'ask_city_mulk'
            await update.message.reply_text("⏰ تذكير سورة الملك بعد العشاء 🤍\n\nابعت اسم مدينتك 👇", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "⏰ تذكير الواقعة":
        if user_id in user_city:
            city = user_city[user_id]
            hour, minute = await schedule_waqia_after_fajr(context, chat_id, user_id, city)
            await ensure_daily_update_job(context, chat_id)
            await update.message.reply_text(f"✅ تم تفعيل تذكير سورة الواقعة!\n\n📍 مدينتك: {city}\n🕌 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        else:
            context.user_data['mode'] = 'ask_city_waqia'
            await update.message.reply_text("⏰ تذكير سورة الواقعة بعد الفجر 🤍\n\nابعت اسم مدينتك 👇", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 القائمة الرئيسية")]], resize_keyboard=True))
        return

    if text == "⏰ تذكير الكهف":
        try:
            import datetime
            for j in context.job_queue.get_jobs_by_name(f"kahf_{chat_id}"):
                j.schedule_removal()
            context.job_queue.run_daily(send_kahf_reminder, time=datetime.time(hour=10, minute=0), days=(4,), chat_id=chat_id, name=f"kahf_{chat_id}")
            await update.message.reply_text("✅ تم تفعيل تذكير سورة الكهف!\n\nكل يوم جمعة الساعة 10 صباحا هبعتلك سورة الكهف كاملة 🕌")
        except:
            await update.message.reply_text("التذكير مش شغال في الاستضافة دي، جرب تاني بعد شوية")
        return

    if text == "❌ إلغاء التذكير":
        try:
            for j in context.job_queue.get_jobs_by_name(str(chat_id)):
                j.schedule_removal()
            await update.message.reply_text("تم إلغاء تذكير سورة الملك ❌")
        except:
            await update.message.reply_text("مفيش تذكير شغال حاليا")
        return

    if text == "❌ إلغاء التذكيرات":
        try:
            for name in [f"mulk_{chat_id}", f"waqia_{chat_id}", f"kahf_{chat_id}", f"sabah_{chat_id}", f"masa_{chat_id}", f"prayer_update_{chat_id}"]:
                for j in context.job_queue.get_jobs_by_name(name):
                    j.schedule_removal()
            await update.message.reply_text("تم إلغاء كل التذكيرات ❌\n(الملك - الواقعة - الكهف - أذكار الصباح - أذكار المساء)")
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

    if context.user_data.get('mode') == 'ask_city_sabah':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد الفجر في {city} ...")
        hour, minute = await schedule_sabah_after_fajr(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(f"✅ تم تفعيل تذكير أذكار الصباح!\n\n📍 مدينتك: {city}\n🌅 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        return

    if context.user_data.get('mode') == 'ask_city_masa':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد العصر في {city} ...")
        hour, minute = await schedule_masa_after_asr(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(f"✅ تم تفعيل تذكير أذكار المساء!\n\n📍 مدينتك: {city}\n🌙 هيبعتلك بعد العصر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        return

    if context.user_data.get('mode') == 'ask_city_mulk':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد العشاء في {city} ...")
        hour, minute = await schedule_mulk_after_isha(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(f"✅ تم تفعيل تذكير سورة الملك!\n\n📍 مدينتك: {city}\n🕌 هيبعتلك بعد العشاء بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        return

    if context.user_data.get('mode') == 'ask_city_waqia':
        city = text.strip()
        user_city[user_id] = city
        context.user_data['mode'] = None
        await update.message.reply_text(f"جاري معرفة معاد الفجر في {city} ...")
        hour, minute = await schedule_waqia_after_fajr(context, chat_id, user_id, city)
        await ensure_daily_update_job(context, chat_id)
        await update.message.reply_text(f"✅ تم تفعيل تذكير سورة الواقعة!\n\n📍 مدينتك: {city}\n🕌 هيبعتلك بعد الفجر بـ 15 دقيقة (الساعة {hour:02d}:{minute:02d})", reply_markup=main_keyboard())
        return

    if context.user_data.get('mode') == 'search_ayah':
        await do_search_ayah(text, update)
        return

    if text in SURAHS:
        n = SURAHS.index(text) + 1
        mode = context.user_data.get('mode', 'read')
        code = user_reciter.get(user_id, "ar.abdulbasitmurattal")
        # اسم القارئ والنوع للعرض
        reciter_name = "عبدالباسط عبدالصمد"
        style_name = ""
        for _s, _styles in SHEIKHS.items():
            for _st, _c in _styles.items():
                if _c == code:
                    reciter_name = _s
                    style_name = _st

        if code == "ar.muhammadrafat" and text not in RIFAAT_SURAHS:
            await update.message.reply_text(f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت\n\nاختر سورة من القايمة دي 👇", reply_markup=rifaat_keyboard())
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

        msg = await update.message.reply_text(f"لقد اخترت سورة {text} من القارئ {reciter_name} - {style_name} برواية حفص عن عاصم، جاري التحميل ..")
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
                f"• القارئ: {reciter_name} - {style_name}\n\n"
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
            await update.message.reply_text(f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت حاليا\nجرب سورة تانية، أو اسمعها بصوت عبدالباسط 👇")
            try:
                await update.message.reply_audio(audio=f"https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/{n}.mp3", title=text, performer="عبدالباسط عبدالصمد", caption=f"🎧 سورة {text} - عبدالباسط عبدالصمد")
            except:
                pass
        else:
            try:
                await update.message.reply_audio(audio=audio_url, title=text, performer=f"{reciter_name} - {style_name}", caption=f"🎧 سورة {text} - {reciter_name} - {style_name}")
            except Exception as e:
                print(f"Audio error {reciter_name} {style_name} surah {n}: {e} - URL was: {audio_url}")
                if code == "ar.muhammadrafat":
                    await update.message.reply_text(f"⚠️ سورة {text} مش متوفرة بصوت الشيخ محمد رفعت حاليا")
                    try:
                        await update.message.reply_audio(audio=f"https://cdn.islamic.network/quran/audio-surah/128/ar.abdulbasitmurattal/{n}.mp3", title=text, performer="عبدالباسط عبدالصمد", caption=f"🎧 سورة {text} - عبدالباسط عبدالصمد")
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

# ================= اختيار القارئ - خطوتين: شيخ -> نوع =================
async def reciter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_sheikhs":
        await query.edit_message_text("🎙️ اختر الشيخ:", reply_markup=sheikhs_keyboard())
        return

    if data.startswith("sheikh:"):
        sheikh = data.split(":", 1)[1]
        await query.edit_message_text(f"🎙️ الشيخ: {sheikh}\n\nاختر نوع التلاوة 👇", reply_markup=styles_keyboard(sheikh))
        return

    if data.startswith("style:"):
        _, sheikh, style = data.split(":", 2)
        code = SHEIKHS[sheikh][style]
        user_reciter[query.from_user.id] = code
        await query.edit_message_text(f"✅ تم اختيار:\n🎙️ الشيخ: {sheikh}\n🎧 النوع: {style}\n\nالآن اختر السورة 👇")
        if code == "abdulbasit_rare":
            await query.message.reply_text("اختر التلاوة النادرة 👇", reply_markup=rare_keyboard())
        elif code == "ar.muhammadrafat":
            await query.message.reply_text("⚠️ الشيخ محمد رفعت ليه سور معينة بس\nاختر من السور المتوفرة 👇", reply_markup=rifaat_keyboard())
        else:
            await query.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

    if data.startswith("reciter:"):
        code = data.split(":", 1)[1]
        user_reciter[query.from_user.id] = code
        await query.edit_message_text(f"تم اختيار القارئ ✅\nالآن اختر السورة:")
        await query.message.reply_text("اختر السورة 👇", reply_markup=surah_keyboard())
        return

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_cmd))
    app.add_handler(CommandHandler("prayer", prayer_cmd))
    app.add_handler(CommandHandler("setcity", setcity_cmd))
    app.add_handler(CallbackQueryHandler(reciter_callback, pattern="^(sheikh:|style:|back_sheikhs|reciter:)"))
    app.add_handler(CallbackQueryHandler(feature_callback, pattern="^feat:"))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot is running...")
    app.run_polling()
