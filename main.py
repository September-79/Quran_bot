import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= الإعدادات =================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@SEPTEMBER_Movies_TV_shows"
CHANNEL_LINK = "https://t.me/SEPTEMBER_Movies_TV_shows"

# ================= فحص الاشتراك الإجباري =================
async def check_sub(update, context):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Check sub error: {e}")
        return False

async def send_sub_message(update, context, is_callback=False):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحققت | اضغط هنا", callback_data="check_sub")]
    ]
    text = (
        "⚠️ عشان تستخدم البوت لازم تشترك في قناتنا الأول 👇\n\n"
        "بعد ما تشترك دوس على ( تحققت )"
    )
    if is_callback:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def check_sub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_sub(update, context):
        await query.edit_message_text(
            "✅ تم التحقق، أهلاً بيك في البوت 🤍\n\n"
            "دوس /start عشان تبدأ"
        )
    else:
        await query.answer("❌ لسه مشتركتش، اشترك الأول ودوس تحقق", show_alert=True)

# ================= قائمة السور =================
SURAHS = [
    (1, "الفاتحة"), (2, "البقرة"), (3, "آل عمران"), (4, "النساء"), (5, "المائدة"),
    (36, "يس"), (55, "الرحمن"), (56, "الواقعة"), (67, "الملك"), (78, "النبأ"),
    (112, "الإخلاص"), (113, "الفلق"), (114, "الناس")
]

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📖 القرآن الكريم", callback_data="menu_quran")],
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="azkar_sabah"),
         InlineKeyboardButton("🌙 أذكار المساء", callback_data="azkar_masa")],
        [InlineKeyboardButton("📿 آية اليوم", callback_data="ayah_today")],
        [InlineKeyboardButton("📢 قناتنا", url=CHANNEL_LINK)],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1 - فحص الاشتراك الإجباري
    if not await check_sub(update, context):
        await send_sub_message(update, context)
        return

    # 2 - لو مشترك، اظهر القائمة
    text = (
        "🤍 أهلاً بيك في بوت القرآن الكريم\n"
        "رفيقك اليومي مع كتاب الله\n\n"
        "📖 قراءة أي سورة\n"
        "🎧 استماع بأصوات القراء\n"
        "📖 تفسير وفضل السورة\n"
        "🌅 أذكار الصباح والمساء\n\n"
        "اختار من القائمة 👇"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())

# ================= قائمة السور =================
async def show_surahs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await check_sub(update, context):
        await send_sub_message(update, context, is_callback=True)
        return

    keyboard = []
    row = []
    for num, name in SURAHS:
        row.append(InlineKeyboardButton(f"{name}", callback_data=f"surah_{num}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_home")])
    await query.edit_message_text("📖 اختار السورة 👇", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= عرض السورة =================
async def show_surah_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await check_sub(update, context):
        await send_sub_message(update, context, is_callback=True)
        return

    surah_num = int(query.data.split("_")[1])
    surah_name = dict(SURAHS).get(surah_num, "")

    keyboard = [
        [InlineKeyboardButton("📖 قراءة السورة", url=f"https://quran.com/{surah_num}")],
        [InlineKeyboardButton("🎧 استماع - مشاري العفاسي", url=f"https://everyayah.com/data/Alafasy_128kbps/{str(surah_num).zfill(3)}001.mp3")],
        [InlineKeyboardButton("📖 التفسير", url=f"https://quran.com/{surah_num}?translations=20")],
        [InlineKeyboardButton("🔙 رجوع للسور", callback_data="menu_quran")],
    ]
    await query.edit_message_text(
        f"📖 سورة {surah_name}\n\nاختار اللي انت عايزه 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= الأذكار و آية اليوم =================
async def azkar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await check_sub(update, context):
        await send_sub_message(update, context, is_callback=True)
        return

    if query.data == "azkar_sabah":
        text = "🌅 أذكار الصباح\n\n1- آية الكرسي\n2- سورة الإخلاص 3 مرات\n3- سورة الفلق 3 مرات\n4- سورة الناس 3 مرات\n5- أصبحنا وأصبح الملك لله..."
    else:
        text = "🌙 أذكار المساء\n\n1- آية الكرسي\n2- سورة الإخلاص 3 مرات\n3- سورة الفلق 3 مرات\n4- سورة الناس 3 مرات\n5- أمسينا وأمسى الملك لله..."

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
    )

async def ayah_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await check_sub(update, context):
        await send_sub_message(update, context, is_callback=True)
        return
    try:
        r = requests.get("https://api.alquran.cloud/v1/ayah/random", timeout=10).json()
        ayah = r['data']['text']
        surah = r['data']['surah']['name']
        num = r['data']['numberInSurah']
        text = f"📿 آية اليوم\n\n{ayah}\n\n— سورة {surah} - آية {num}"
    except:
        text = "📿 آية اليوم\n\n﴿ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ ﴾\n\n— سورة الرعد"
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
    )

async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤍 أهلاً بيك في بوت القرآن الكريم\n\nاختار من القائمة 👇",
        reply_markup=main_menu_keyboard()
    )

# ================= تشغيل البوت =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_button, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(show_surahs, pattern="^menu_quran$"))
    app.add_handler(CallbackQueryHandler(show_surah_detail, pattern="^surah_"))
    app.add_handler(CallbackQueryHandler(azkar_handler, pattern="^azkar_"))
    app.add_handler(CallbackQueryHandler(ayah_today, pattern="^ayah_today$"))
    app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
