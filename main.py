from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import datetime, os
from keep_alive import keep_alive

ADMIN_ID = 6243881362  # আপনার টেলিগ্রাম ইউজার আইডি এখানে বসান
GROUP_IDS = [-1002560574306, -1002622279798, -1002676258756]

# ইউজার আইডি সংরক্ষণ
def save_user_id(user_id):
    with open("user_ids.txt", "a+") as f:
        f.seek(0)
        ids = f.read().splitlines()
        if str(user_id) not in ids:
            f.write(str(user_id) + "\n")

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_id(user.id)

    keyboard = [
        [InlineKeyboardButton("✅ Joined", callback_data='check_join')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""স্বাগতম {user.first_name}!
Bangla Quiz Hub - আপনার জ্ঞান বৃদ্ধির এক অনন্য প্ল্যাটফর্মে আপনাকে স্বাগতম!

**শুরু করার আগে নিচের ৩টি গ্রুপে জয়েন করুন:**  
1. [Gen Z 078](https://t.me/gen_z078)  
2. [Trick BD 07](https://t.me/trick_bd07)  
3. [Swygen](https://t.me/swygen)

গ্রুপে জয়েন করার পর "✅ Joined" বাটনে ক্লিক করুন।
"""
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Check Join
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    joined_all = all(
        (await context.bot.get_chat_member(group_id, user_id)).status not in ['left', 'kicked']
        for group_id in GROUP_IDS
    )

    if joined_all:
        keyboard = [
            [InlineKeyboardButton("👤 Profile", callback_data='profile')],
            [InlineKeyboardButton("🔗 Share", callback_data='share')],
            [InlineKeyboardButton("🌐 Website", callback_data='website')],
            [InlineKeyboardButton("🛠 Support", callback_data='support')],
        ]
        await update.callback_query.message.reply_text("✅ আপনি সফলভাবে সব গ্রুপে জয়েন করেছেন।", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.reply_text("❌ দয়া করে আগে সবগুলো গ্রুপে জয়েন করুন এবং আবার চেষ্টা করুন।")

# Callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if query.data == 'profile':
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        await query.message.reply_text(f"👤 নাম: {user.first_name}\n🆔 ইউজার আইডি: {user.id}\n📅 জয়েন তারিখ: {date}\n🌍 বাংলাদেশি")
    elif query.data == 'share':
        await query.message.reply_text("Bangla Quiz Hub আপনার বন্ধুদের সাথে শেয়ার করুন এবং তাদের কেউ জ্ঞান অর্জন এর সুযোগ করে দিন!\n\n🔗 রেফার লিংক: https://t.me/YourBotUsername?start=")
    elif query.data == 'website':
        await query.message.reply_text("🌐 Bangla Quiz Hub: https://bangla-quiz-hub.netlify.app/")
    elif query.data == 'support':
        await query.message.reply_text("সাহায্যের জন্য যোগাযোগ করুন: @Swygen_bd")

# Broadcast: Admin Command
broadcast_state = {}

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("আপনার অনুমতি নেই।")
    broadcast_state[update.effective_user.id] = 'awaiting'
    await update.message.reply_text("কি পাঠাতে চান? শুধু টেক্সট লিখুন অথবা একটি ছবি পাঠান ইনলাইন বাটনসহ।")

# Handle Broadcast Message or Photo
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or broadcast_state.get(update.effective_user.id) != 'awaiting':
        return

    with open("user_ids.txt") as f:
        ids = [int(i.strip()) for i in f if i.strip().isdigit()]

    keyboard = InlineKeyboardMarkup(InlineKeyboardButton("🌐 Visit Website", url="https://bangla-quiz-hub.netlify.app"))

    for uid in ids:
        try:
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                await context.bot.send_photo(uid, photo=file_id, caption=update.message.caption, reply_markup=keyboard)
            else:
                await context.bot.send_message(uid, update.message.text, reply_markup=keyboard)
        except:
            continue

    await update.message.reply_text("✅ সকল ইউজারকে নোটিফিকেশন পাঠানো হয়েছে।")
    broadcast_state.pop(update.effective_user.id, None)

# Main
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token("7772481310:AAFbajzs75hBtuNzPTHd7Ygbj8ij9cRA8Xs").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(check_join, pattern='check_join'))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_broadcast))
    print("Bot is running...")
    app.run_polling()
