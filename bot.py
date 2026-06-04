import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import *
import database as db
from shop_data import SHOP_CATEGORIES, get_product, get_all_products

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== لوحات المفاتيح =====================

def main_keyboard():
    """لوحة المفاتيح الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="home"),
         InlineKeyboardButton("🪙 نقاطي", callback_data="my_points"),
         InlineKeyboardButton("💰 رصيدي", callback_data="my_balance")],
        [InlineKeyboardButton("🛒 المتجر", callback_data="shop"),
         InlineKeyboardButton("🎁 استبدال نقاط", callback_data="redeem_menu")],
        [InlineKeyboardButton("📅 مكافأة يومية", callback_data="daily"),
         InlineKeyboardButton("👥 إحالة الأصدقاء", callback_data="referral")],
        [InlineKeyboardButton("🏆 ترتيب النقاط", callback_data="leaderboard"),
         InlineKeyboardButton("💸 تحويل نقاط", callback_data="transfer_points")],
        [InlineKeyboardButton("📜 سجل عملياتي", callback_data="history"),
         [InlineKeyboardButton("❓ مساعدة", callback_data="help"),
          InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")]]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    """لوحة تحكم الأدمن"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة نقاط", callback_data="admin_add_points")],
        [InlineKeyboardButton("💰 إضافة رصيد", callback_data="admin_add_balance")],
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban")],
        [InlineKeyboardButton("🔓 إلغاء حظر", callback_data="admin_unban")],
        [InlineKeyboardButton("🎁 إنشاء كود خصم", callback_data="admin_coupon")],
        [InlineKeyboardButton("📢 إشعار عام", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="home")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===================== الأوامر الرئيسية =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب عند بدء البوت"""
    user = update.effective_user
    args = context.args
    referrer_id = None
    
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id == user.id:
            referrer_id = None
    
    # التحقق من وجود المستخدم
    existing = db.get_user(user.id)
    if not existing:
        db.create_user(user.id, user.username, user.first_name, referrer_id)
        welcome_points = 25
        db.update_points(user.id, welcome_points, "نقاط ترحيبية")
    
    welcome_text = f"""
🔥 *أهلاً وسهلاً بك، {user.first_name}!* 🔥
╔════════════════════════╗
║     𝗛𝗔𝗥𝗕𝗜 🇸🇾🦅          ║
║  أقوى منصة مكافآت وعروض  ║
╚════════════════════════╝

⭐️ *تم منحك 25 نقطة ترحيبية!* ⭐️

✨ *ماذا يمكنك أن تفعل؟*
• 🪙 اجمع النقاط يومياً
• 🛒 استبدل نقاطك بمنتجات حصرية
• 💰 حول رصيدك إلى نقاط
• 👥 اربح نقاطاً بدعوة أصدقائك

📢 *قناة العروض:* {CHANNEL_LINK}
🆘 *الدعم الفني:* {SUPPORT_LINK}

👇 *اختر القسم المناسب من الأزرار أدناه*
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة إلى القائمة الرئيسية"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    text = f"""
🔥 *مرحباً بك في القائمة الرئيسية يا {user.first_name}!* 🔥

🪙 *نقاطك:* {db.get_user(user.id)['points']}
💰 *رصيدك:* {db.get_user(user.id)['balance']} ل.س

👇 *اختر ما تريد:*
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض نقاط المستخدم"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    text = f"""
╔════════════════════════╗
║       🪙 *نقاطي*        ║
╚════════════════════════╝

✨ *رصيد نقاطك الحالي:* `{user['points']}` نقطة

📊 *إحصائياتك:*
• 💰 إجمالي ما أنفقته: {user['total_spent_points']} نقطة
• 🎁 عدد المشتريات: {user['total_purchases']} عملية

💡 *طرق كسب النقاط:*
• 📅 المكافأة اليومية: +{DAILY_REWARD} نقطة
• 👥 دعوة الأصدقاء: +{REFERRAL_REWARD} نقطة لكل صديق
• 🛒 شراء النقاط: {POINTS_PRICE} ل.س = 1 نقطة
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رصيد المستخدم"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    text = f"""
╔════════════════════════╗
║      💰 *رصيدي*         ║
╚════════════════════════╝

✨ *رصيدك الحالي:* `{user['balance']}` ل.س

💡 *طرق استخدام الرصيد:*
• 🛒 شراء نقاط: 1 نقطة = {POINTS_PRICE} ل.س
• 💸 سحب الرصيد (الحد الأدنى: {MIN_WITHDRAW} ل.س)

📞 *للسحب أو الشحن:* تواصل مع الدعم الفني
{SUPPORT_LINK}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المكافأة اليومية"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if db.claim_daily(user_id):
        text = f"""
✅ *تم منحك المكافأة اليومية!*

🎁 +{DAILY_REWARD} نقطة

📅 *عود غداً لمزيد من النقاط*
💪 استمر في جمع النقاط يومياً لمكافآت أكبر!
"""
    else:
        user = db.get_user(user_id)
        text = f"""
❌ *لقد حصلت على مكافأتك اليوم مسبقاً!*

🕐 *عود غداً*
📅 آخر مكافأة: {user['last_daily']}

💡 لا تنسى العودة غداً للحصول على {DAILY_REWARD} نقطة إضافية!
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المتجر بالأقسام"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for emoji, cat in SHOP_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat['name']}", callback_data=f"cat_{emoji}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="home")])
    
    await query.edit_message_text(
        "🛒 *مرحباً بك في متجر HARBI!*\n\nاختر القسم الذي تريد:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض منتجات فئة معينة"""
    query = update.callback_query
    await query.answer()
    category_emoji = query.data.replace("cat_", "")
    cat = SHOP_CATEGORIES.get(category_emoji)
    
    if not cat:
        return
    
    keyboard = []
    for product in cat["products"]:
        price_text = f"{product['points']} نقطة"
        if product['balance'] > 0:
            price_text += f" أو {product['balance']} ل.س"
        keyboard.append([InlineKeyboardButton(f"{product['name']} - {price_text}", callback_data=f"buy_{product['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="shop")])
    
    await query.edit_message_text(
        f"📦 *{cat['name']}*\n\nاختر المنتج الذي تريد شراءه:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شراء منتج"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    product_id = query.data.replace("buy_", "")
    product = get_product(product_id)
    
    if not product:
        await query.edit_message_text("❌ المنتج غير موجود!", reply_markup=main_keyboard())
        return
    
    user = db.get_user(user_id)
    
    # التحقق من الرصيد
    if product['points'] > 0 and user['points'] >= product['points']:
        # شراء بالنقاط
        db.update_points(user_id, -product['points'], f"شراء {product['name']}")
        db.update_points(user_id, 0, "")  # تحديث total_purchases
        # تحديث عدد المشتريات
        conn = db.get_db()
        conn.execute("UPDATE users SET total_purchases = total_purchases + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        text = f"""
✅ *تم شراء المنتج بنجاح!*

🎁 *المنتج:* {product['name']}
🔻 *الخصم:* {product['points']} نقطة
🪙 *نقاطك المتبقية:* {user['points'] - product['points']}

📦 *تفاصيل المنتج:* {product['details']}

📞 *سيتم التواصل معك قريباً لتسليم المنتج*
{SUPPORT_LINK}
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())
        
    elif product['balance'] > 0 and user['balance'] >= product['balance']:
        # شراء بالرصيد
        db.update_balance(user_id, -product['balance'], f"شراء {product['name']}")
        
        text = f"""
✅ *تم شراء المنتج بنجاح!*

🎁 *المنتج:* {product['name']}
🔻 *الخصم:* {product['balance']} ل.س
💰 *رصيدك المتبقي:* {user['balance'] - product['balance']} ل.س

📦 *تفاصيل المنتج:* {product['details']}

📞 *سيتم التواصل معك قريباً لتسليم المنتج*
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        text = f"""
❌ *رصيدك لا يكفي لشراء هذا المنتج!*

🎁 *المنتج:* {product['name']}
💰 *السعر:* {product['points']} نقطة أو {product['balance']} ل.س

🪙 *نقاطك:* {user['points']}
💰 *رصيدك:* {user['balance']} ل.س

💡 *طرق زيادة الرصيد:*
• 📅 احصل على المكافأة اليومية
• 👥 ادعُ أصدقاءك
• 💰 اشحن رصيدك عبر الدعم الفني
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def referral_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نظام الإحالة"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={user_id}"
    
    text = f"""
╔════════════════════════╗
║      👥 *الإحالة*       ║
╚════════════════════════╝

🎁 *عند دعوة صديق:*
• 🎉 *أنت تكسب:* +{REFERRAL_REWARD} نقطة
• 🎉 *صديقك يكسب:* +{REFERRED_REWARD} نقطة

🔗 *رابط الإحالة الخاص بك:*
`{link}`

📤 *انسخ الرابط وأرسله لأصدقائك!*

📊 *عدد من دعوتهم:* قريباً
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ترتيب المستخدمين حسب النقاط"""
    query = update.callback_query
    await query.answer()
    
    leaders = db.get_leaderboard(10)
    
    text = "🏆 *قائمة الأغنياء في HARBI* 🏆\n\n"
    
    if not leaders:
        text += "لا يوجد مستخدمين بعد. كن أنت الأول! 🚀"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, user in enumerate(leaders):
            medal = medals[i] if i < 3 else f"{i+1}."
            name = user['first_name'] or user['username'] or f"مستخدم {user['user_id']}"
            if len(name) > 15:
                name = name[:12] + "..."
            text += f"{medal} *{name}* → 🪙 {user['points']} نقطة\n"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def transfer_points_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة تحويل النقاط"""
    query = update.callback_query
    await query.answer()
    
    text = """
💸 *تحويل النقاط*

📝 *لتحويل النقاط到一个 صديق:*
أرسل الأمر التالي:
`/transfer [معرف المستخدم] [عدد النقاط]`

📌 *مثال:*
`/transfer 123456789 100`

⚠️ *ملاحظات:*
• الحد الأدنى للتحويل: 10 نقاط
• لا يمكن استرداد النقاط بعد التحويل
• لا يمكن التحويل إلى نفسك
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنفيذ تحويل النقاط"""
    sender_id = update.effective_user.id
    
    try:
        receiver_id = int(context.args[0])
        points = int(context.args[1])
        
        if points < 10:
            await update.message.reply_text("❌ الحد الأدنى للتحويل هو 10 نقاط.")
            return
        
        if sender_id == receiver_id:
            await update.message.reply_text("❌ لا يمكنك تحويل النقاط لنفسك!")
            return
        
        sender = db.get_user(sender_id)
        receiver = db.get_user(receiver_id)
        
        if not receiver:
            await update.message.reply_text("❌ المعرف الذي أدخلته غير مسجل في البوت!")
            return
        
        if sender['points'] < points:
            await update.message.reply_text(f"❌ نقاطك لا تكفي!\nلديك {sender['points']} نقطة وتحتاج {points} نقطة.")
            return
        
        # تنفيذ التحويل
        db.update_points(sender_id, -points, f"تحويل {points} نقطة إلى المستخدم {receiver_id}")
        db.update_points(receiver_id, points, f"استلام {points} نقطة من المستخدم {sender_id}")
        
        receiver_name = receiver['first_name'] or receiver['username'] or str(receiver_id)
        
        await update.message.reply_text(
            f"✅ *تم تحويل {points} نقطة بنجاح!*\n\n"
            f"👤 *إلى:* {receiver_name}\n"
            f"🪙 *نقاطك المتبقية:* {sender['points'] - points}\n\n"
            f"💪 استمر في جمع النقاط للمزيد!",
            parse_mode="Markdown"
        )
        
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ *خطأ في الصيغة!*\n\n"
            "الاستخدام الصحيح:\n`/transfer [معرف المستخدم] [النقاط]`\n\n"
            "مثال: `/transfer 123456789 100`",
            parse_mode="Markdown"
        )

async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """سجل المعاملات"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    transactions = db.get_user_transactions(user_id, 15)
    
    if not transactions:
        text = "📜 *ليس لديك أي عمليات سابقة حتى الآن*\n\nابدأ بجمع النقاط واستبدالها اليوم!"
    else:
        text = "📜 *سجل عملياتك الأخيرة:*\n\n"
        for t in transactions:
            date = t['date'][:16] if t['date'] else ""
            if t['type'] == 'points':
                sign = "+" if t['amount'] > 0 else ""
                text += f"🪙 {sign}{t['amount']} نقطة - {t['description']}\n📅 {date}\n\n"
            elif t['type'] == 'balance':
                sign = "+" if t['amount'] > 0 else ""
                text += f"💰 {sign}{t['amount']} ل.س - {t['description']}\n📅 {date}\n\n"
            else:
                text += f"📌 {t['description']}\n📅 {date}\n\n"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة المساعدة"""
    query = update.callback_query
    await query.answer()
    
    text = f"""
❓ *مركز المساعدة - HARBI*

📌 *الأوامر المتاحة:*
• /start - بدء البوت
• /transfer - تحويل النقاط

🪙 *كسب النقاط:*
• المكافأة اليومية: +{DAILY_REWARD} نقطة
• دعوة الأصدقاء: +{REFERRAL_REWARD} نقطة لكل صديق
• شراء النقاط: {POINTS_PRICE} ل.س = 1 نقطة

🛒 *استخدام النقاط:*
• شراء بطاقات شحن
• شراء خدمات رقمية
• تحويل لأصدقائك

📞 *الدعم الفني:* {SUPPORT_LINK}
📢 *قناة العروض:* {CHANNEL_LINK}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معلومات عن البوت"""
    query = update.callback_query
    await query.answer()
    
    total_users = db.get_all_users_count()
    total_points = db.get_total_points()
    
    text = f"""
ℹ️ *عن بوت HARBI*

⭐ *الإصدار:*
