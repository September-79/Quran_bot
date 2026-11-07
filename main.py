import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","ابراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الانسان","المرسلات","النبأ","النازعات","عبس","التكوير","الإنفطار","المطففين","الإنشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# فضل وسبب نزول السور المشهورة
SURAH_INFO = {
    "الفاتحة": {"virtue": "أعظم سورة في القرآن، وهي السبع المثاني، لا تصح الصلاة إلا بها.", "reason": "نزلت بمكة، وهي أول سورة كاملة نزلت."},
    "البقرة": {"virtue": "أخذها بركة وتركها حسرة، ولا تستطيعها البطلة (السحرة). فيها آية الكرسي أعظم آية.", "reason": "نزلت بالمدينة، وهي أول سورة نزلت بالمدينة، وفيها أحكام الصيام والحج والطلاق."},
    "آل عمران": {"virtue": "تأتي يوم القيامة تحاج عن صاحبها مع البقرة كأنهما غمامتان.", "reason": "نزلت بالمدينة بعد غزوة أحد، وفيها الرد على نصارى نجران."},
    "النساء": {"virtue": "فيها أحكام المواريث والنساء واليتامى والجهاد.", "reason": "نزلت بالمدينة بعد أحد، وسميت بسورة النساء الكبرى."},
    "المائدة": {"virtue": "آخر ما نزل من السور، فيها تحريم الخمر والميسر.", "reason": "نزلت بالمدينة، ونزلت فيها آية إكمال الدين."},
    "الأنعام": {"virtue": "نزلت جملة واحدة يشيعها سبعون ألف ملك.", "reason": "نزلت بمكة، وفيها التوحيد والرد على المشركين."},
    "الأعراف": {"virtue": "فيها قصة آدم وإبليس وأصحاب الأعراف.", "reason": "نزلت بمكة، وسميت بالأعراف لذكر أصحاب الأعراف فيها."},
    "الأنفال": {"virtue": "فيها أحكام الغنائم وغزوة بدر.", "reason": "نزلت بالمدينة بعد غزوة بدر الكبرى."},
    "التوبة": {"virtue": "هي الفاضحة، فضحت المنافقين. وهي السورة الوحيدة بدون بسملة.", "reason": "نزلت بالمدينة في غزوة تبوك، وسميت براءة."},
    "يونس": {"virtue": "فيها قصة يونس وقومه الذين آمنوا فمتعهم الله.", "reason": "نزلت بمكة."},
    "هود": {"virtue": "شيبتني هود وأخواتها، لما فيها من أهوال يوم القيامة.", "reason": "نزلت بمكة، وفيها قصص الأنبياء."},
    "يوسف": {"virtue": "أحسن القصص، فيها العبرة والصبر والفرج بعد الكرب.", "reason": "نزلت بمكة في عام الحزن تسلية للنبي ﷺ."},
    "الرعد": {"virtue": "فيها عظمة خلق الله والرعد يسبح بحمده.", "reason": "نزلت بالمدينة، وقيل مكية."},
    "ابراهيم": {"virtue": "فيها دعاء إبراهيم لمكة وأهلها.", "reason": "نزلت بمكة."},
    "الحجر": {"virtue": "فيها حفظ الله للقرآن: إنا نحن نزلنا الذكر وإنا له لحافظون.", "reason": "نزلت بمكة."},
    "النحل": {"virtue": "سميت سورة النعم لكثرة النعم المذكورة فيها.", "reason": "نزلت بمكة."},
    "الإسراء": {"virtue": "فيها قصة الإسراء والمعراج وبر الوالدين.", "reason": "نزلت بمكة قبل الهجرة بسنة."},
    "الكهف": {"virtue": "من قرأها يوم الجمعة أضاء له من النور ما بين الجمعتين، وعصم من فتنة الدجال.", "reason": "نزلت بمكة لما سأل المشركون عن أهل الكهف وذي القرنين."},
    "مريم": {"virtue": "فيها قصة مريم وولادة عيسى ويحيى وزكريا.", "reason": "نزلت بمكة."},
    "طه": {"virtue": "ما أنزلنا عليك القرآن لتشقى، فيها قصة موسى.", "reason": "نزلت بمكة، وكان عمر بن الخطاب سبب إسلامه سماعها."},
    "الأنبياء": {"virtue": "فيها قصص 16 نبيا، وهي سورة الأنبياء.", "reason": "نزلت بمكة."},
    "الحج": {"virtue": "فيها أحكام الحج والجهاد، وهي من أعاجيب السور فيها سجدتان.", "reason": "نزلت بالمدينة، وقيل مختلطة."},
    "المؤمنون": {"virtue": "فيها صفات المؤمنين المفلحين أولها قد أفلح المؤمنون.", "reason": "نزلت بمكة."},
    "النور": {"virtue": "فيها آية النور، الله نور السماوات والأرض، وأحكام العفاف.", "reason": "نزلت بالمدينة في حادثة الإفك."},
    "الفرقان": {"virtue": "فيها صفات عباد الرحمن.", "reason": "نزلت بمكة."},
    "يس": {"virtue": "قلب القرآن، من قرأها كتب له بقراءتها قراءة القرآن عشر مرات.", "reason": "نزلت بمكة."},
    "الرحمن": {"virtue": "عروس القرآن، فيها تكرار فبأي آلاء ربكما تكذبان.", "reason": "نزلت بالمدينة، وقيل مكية."},
    "الواقعة": {"virtue": "من قرأها كل ليلة لم تصبه فاقة أبدا، وهي سورة الغنى.", "reason": "نزلت بمكة، وفيها ذكر أصناف الناس يوم القيامة."},
    "الحديد": {"virtue": "فيها أنزلنا الحديد فيه بأس شديد ومنافع للناس.", "reason": "نزلت بالمدينة."},
    "الحشر": {"virtue": "فيها آخر آيات: لو أنزلنا هذا القرآن على جبل لرأيته خاشعا.", "reason": "نزلت بالمدينة في غزوة بني النضير."},
    "الجمعة": {"virtue": "تقرأ في صلاة الجمعة، فيها فضل يوم الجمعة.", "reason": "نزلت بالمدينة."},
    "الملك": {"virtue": "سورة تشفع لصاحبها، من قرأها كل ليلة منجية من عذاب القبر.", "reason": "نزلت بمكة."},
    "القلم": {"virtue": "أول ما خلق الله القلم، وفيها وإنك لعلى خلق عظيم.", "reason": "نزلت بمكة، وهي ثاني سورة نزلت بعد العلق."},
    "الحاقة": {"virtue": "فيها أهوال يوم القيامة والحاقة ما الحاقة.", "reason": "نزلت بمكة."},
    "نوح": {"virtue": "فيها دعوة نوح لقومه ألف سنة إلا خمسين عاما.", "reason": "نزلت بمكة."},
    "الجن": {"virtue": "فيها استماع الجن للقرآن وإيمانهم به.", "reason": "نزلت بمكة لما عاد النبي ﷺ من الطائف."},
    "المزمل": {"virtue": "فيها قيام الليل: قم الليل إلا قليلا.", "reason": "نزلت بمكة في بداية الدعوة."},
    "المدثر": {"virtue": "فيها يا أيها المدثر قم فأنذر.", "reason": "نزلت بمكة بعد نزول الوحي."},
    "القيامة": {"virtue": "فيها لا أقسم بيوم القيامة، وأهوالها.", "reason": "نزلت بمكة."},
    "الانسان": {"virtue": "تقرأ في فجر الجمعة مع السجدة، فيها جزاء الأبرار.", "reason": "نزلت بالمدينة، وقيل مكية."},
    "النبأ": {"virtue": "فيها ذكر يوم الفصل والجنة والنار.", "reason": "نزلت بمكة."},
    "النازعات": {"virtue": "فيها قصة موسى وفرعون.", "reason": "نزلت بمكة."},
    "عبس": {"virtue": "فيها عتاب النبي ﷺ في ابن أم مكتوم الأعمى.", "reason": "نزلت بمكة لما جاء ابن أم مكتوم والنبي مع سادة قريش."},
    "التكوير": {"virtue": "من سره أن ينظر إلى يوم القيامة رأي العين فليقرأها.", "reason": "نزلت بمكة."},
    "الإنفطار": {"virtue": "من أهوال يوم القيامة، إذا السماء انفطرت.", "reason": "نزلت بمكة."},
    "المطففين": {"virtue": "تحذر من الغش في الميزان، ويل للمطففين.", "reason": "نزلت بالمدينة، وقيل مكية."},
    "الإنشقاق": {"virtue": "فيها انشقاق السماء وأهوال القيامة.", "reason": "نزلت بمكة."},
    "البروج": {"virtue": "فيها قصة أصحاب الأخدود الذين أحرقوا في النار.", "reason": "نزلت بمكة."},
    "الطارق": {"virtue": "فيها والسماء والطارق، والطارق هو النجم الثاقب.", "reason": "نزلت بمكة."},
    "الأعلى": {"virtue": "تقرأ في صلاة العيد والجمعة، سبح اسم ربك الأعلى.", "reason": "نزلت بمكة."},
    "الغاشية": {"virtue": "تقرأ مع الأعلى في الجمعة والعيد.", "reason": "نزلت بمكة."},
    "الفجر": {"virtue": "فيها والفجر وليال عشر، وهي عشر ذي الحجة.", "reason": "نزلت بمكة."},
    "البلد": {"virtvenue": "فيها لا أقسم بهذا البلد، وهو مكة.", "reason": "نزلت بمكة."},
    "الشمس": {"virtue": "فيها والشمس وضحاها، وقصة ثمود.", "reason": "نزلت بمكة."},
    "الليل": {"virtue": "فيها والليل إذا يغشى، وفضل الصدقة.", "reason": "نزلت بمكة."},
    "الضحى": {"virtue": "نزلت تسلية للنبي لما فتر الوحي: ما ودعك ربك وما قلى.", "reason": "نزلت بمكة بعد فتور الوحي."},
    "الشرح": {"virtue": "فيها ألم نشرح لك صدرك، وإن مع العسر يسرا.", "reason": "نزلت بمكة."},
    "التين": {"virtue": "فيها والتين والزيتون، ولقد خلقنا الإنسان في أحسن تقويم.", "reason": "نزلت بمكة."},
    "العلق": {"virtue": "أول ما نزل من القرآن: اقرأ باسم ربك الذي خلق.", "reason": "نزلت بمكة في غار حراء."},
    "القدر": {"virtue": "ليلة القدر خير من ألف شهر، من قامها غفر له.", "reason": "نزلت بمكة."},
    "البينة": {"virtue": "فيها خير البرية وشر البرية.", "reason": "نزلت بالمدينة."},
    "الزلزلة": {"virtue": "تعدل نصف القرآن، فيها إذا زلزلت الأرض زلزالها.", "reason": "نزلت بالمدينة."},
    "العاديات": {"virtue": "فيها والعاديات ضبحا، وهي الخيل في سبيل الله.", "reason": "نزلت بمكة."},
    "القارعة": {"virtue": "فيها القارعة ما القارعة، وموازين الأعمال.", "reason": "نزلت بمكة."},
    "التكاثر": {"virtue": "فيها ألهاكم التكاثر، والتحذير من الانشغال بالدنيا.", "reason": "نزلت بمكة."},
    "العصر": {"virtue": "قال الشافعي: لو تدبرها الناس لوسعتهم، فيها أن الإنسان لفي خسر.", "reason": "نزلت بمكة."},
    "الهمزة": {"virtue": "تحذر من الغيبة والنميمة وجمع المال.", "reason": "نزلت بمكة."},
    "الفيل": {"virtue": "فيها قصة أبرهة وأصحاب الفيل الذين أرادوا هدم الكعبة.", "reason": "نزلت بمكة."},
    "قريش": {"virtue": "فيها نعم الله على قريش برحلة الشتاء والصيف.", "reason": "نزلت بمكة."},
    "الماعون": {"virtue": "تحذر من الرياء ومنع الماعون.", "reason": "نزلت بمكة."},
    "الكوثر": {"virtue": "فيها إنا أعطيناك الكوثر، وهو نهر في الجنة.", "reason": "نزلت بمكة."},
    "الكافرون": {"virtue": "تعدل ربع القرآن، وهي براءة من الشرك، تقرأ قبل النوم.", "reason": "نزلت بمكة لما طلب المشركون المساومة."},
    "النصر": {"virtue": "تعدل ربع القرآن، وهي آخر سورة نزلت كاملة، ونعى فيها للنبي ﷺ.", "reason": "نزلت بالمدينة في حجة الوداع."},
    "المسد": {"virtue": "فيها هلاك أبي لهب وامرأته حمالة الحطب.", "reason": "نزلت بمكة لما آذى أبو لهب النبي ﷺ."},
    "الإخلاص": {"virtue": "تعدل ثلث القرآن، من قرأها 3 مرات كأنما قرأ القرآن كله.", "reason": "نزلت بمكة لما سأل المشركون: صف لنا ربك."},
    "الفلق": {"virtue": "من المعوذتين، ما تعوذ متعوذ بمثلهما، تقرأ صباحا ومساء.", "reason": "نزلت بمكة، وقيل بالمدينة في قصة سحر النبي ﷺ."},
    "الناس": {"virtue": "من المعوذتين، خاتمة القرآن، تحفظ من وسوسة الشيطان.", "reason": "نزلت بمكة، وقيل بالمدينة."},
}

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

            # معلومات + فضل + سبب نزول
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
