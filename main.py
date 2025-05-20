from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import logging
import os

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Replace with your bot token and admin ID ---
BOT_TOKEN = "7772481310:AAFbajzs75hBtuNzPTHd7Ygbj8ij9cRA8Xs"
ADMIN_ID = 6243881362  # Replace with your Telegram ID

# --- Group IDs where user must join ---
GROUP_IDS = [
    -1002560574306,  # @gen_z078
    -1002622279798,  # @trick_bd07
    -1002676258756   # @swygen
]

# --- Dictionary to save join dates ---
user_join_dates = {}

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_join_dates[user.id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    keyboard = [
        [InlineKeyboardButton("✅ Joined", callback_data='check_join')],
        [InlineKeyboardButton("Join Group 1", url="https://t.me/gen_z078")],
        [InlineKeyboardButton("Join Group 2", url="https://t.me/trick_bd07")],
        [InlineKeyboardButton("Join Group 3", url="https://t.me/swygen")],
    ]

    await update.message.reply_text(
        f"স্বাগতম {user.first_name}!\n\nএই বট ব্যবহারের জন্য আপনাকে নিচের ৩টি গ্রুপে জয়েন করতে হবে।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Check Join ---
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        joined_all = all(
            (await context.bot.get_chat_member(group_id, user_id)).status in ['member', 'administrator', 'creator']
            for group_id in GROUP_IDS
        )

        if joined_all:
            keyboard = [
                [InlineKeyboardButton("👤 Profile", callback_data='profile')],
                [InlineKeyboardButton("🔗 Share", callback_data='share')],
                [InlineKeyboardButton("🌐 Website", callback_data='website')],
                [InlineKeyboardButton("🛠 Support", callback_data='support')],
            ]
            await update.callback_query.message.reply_text(
                "✅ আপনি সফলভাবে সব গ্রুপে জয়েন করেছেন!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.callback_query.message.reply_text(
                "❌ দয়া করে সবগুলো গ্রুপে জয়েন করুন এবং আবার চেষ্টা করুন।"
            )
    except Exception as e:
        await update.callback_query.message.reply_text(
            f"⚠️ সমস্যা: `{e}`", parse_mode="Markdown"
        )

# --- Button Handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "profile":
        date = user_join_dates.get(user.id, "অজানা")
        text = f"👤 প্রোফাইল তথ্য\n\nনাম: {user.full_name}\nইউজার আইডি: `{user.id}`\nযোগদান: {date}"
        await query.message.reply_text(text, parse_mode="Markdown")

    elif query.data == "share":
        ref_link = f"https://t.me/YourBotUsername?start={user.id}"
        text = f"📢 Bangla Quiz Hub আপনার বন্ধুদের সাথে শেয়ার করুন এবং তাদের কেউ জ্ঞান অর্জনের সুযোগ দিন!\n\nরেফার লিংক:\n{ref_link}"
        await query.message.reply_text(text)

    elif query.data == "website":
        await query.message.reply_text("🌐 Bangla Quiz Hub আপনার জ্ঞান অর্জনের এক অনন্য সঙ্গী:\nhttps://bangla-quiz-hub.netlify.app/")

    elif query.data == "support":
        await query.message.reply_text("🛠 যেকোনো সমস্যা বা প্রশ্নের জন্য আমাকে মেসেজ করুন:\n@swygen_bd")

# --- Admin Notification Broadcast ---
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ আপনি এই কমান্ড চালাতে পারবেন না।")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("একটি ছবি / টেক্সটের রিপ্লাই দিয়ে `/send` লিখুন।")
        return

    msg = update.message.reply_to_message
    users = list(user_join_dates.keys())

    sent = 0
    for uid in users:
        try:
            if msg.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=msg.photo[-1].file_id,
                    caption=msg.caption or "নোটিফিকেশন",
                    reply_markup=msg.reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=msg.text or msg.caption,
                    reply_markup=msg.reply_markup
                )
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ পাঠানো হয়েছে: {sent} জনকে")

# --- Keep Alive (Optional for Replit) ---
from keep_alive import keep_alive
keep_alive()

# --- Main Function ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", admin_broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    print("✅ Bot is running...")
    app.run_polling()
