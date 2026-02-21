import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")"

BASE_DIR = "projects"
os.makedirs(BASE_DIR, exist_ok=True)

running_process = {}

def user_dir(user_id):
    path = os.path.join(BASE_DIR, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📂 My Files", callback_data="files")],
        [InlineKeyboardButton("▶ Run", callback_data="run")],
        [InlineKeyboardButton("⛔ Stop", callback_data="stop")],
        [InlineKeyboardButton("🔄 Restart", callback_data="restart")]
    ]
    await update.message.reply_text(
        "🚀 Python Hosting Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    folder = user_dir(user_id)

    doc = update.message.document
    file = await doc.get_file()
    file_path = os.path.join(folder, doc.file_name)
    await file.download_to_drive(file_path)

    await update.message.reply_text("✅ File Uploaded Successfully")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    folder = user_dir(user_id)

    await query.answer()

    if query.data == "files":
        files = os.listdir(folder)
        text = "\n".join(files) if files else "No files uploaded."
        await query.edit_message_text(f"📂 Your Files:\n{text}")

    elif query.data == "run":
        main_file = os.path.join(folder, "main.py")
        if not os.path.exists(main_file):
            await query.edit_message_text("⚠ Upload main.py first")
            return

        process = subprocess.Popen(
            ["python3", main_file],
            cwd=folder
        )

        running_process[user_id] = process
        await query.edit_message_text("▶ App Started")

    elif query.data == "stop":
        process = running_process.get(user_id)
        if process:
            process.kill()
            running_process.pop(user_id)
            await query.edit_message_text("⛔ App Stopped")
        else:
            await query.edit_message_text("⚠ No running app")

    elif query.data == "restart":
        process = running_process.get(user_id)
        if process:
            process.kill()

        main_file = os.path.join(folder, "main.py")
        process = subprocess.Popen(
            ["python3", main_file],
            cwd=folder
        )
        running_process[user_id] = process
        await query.edit_message_text("🔄 App Restarted")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, upload_file))
    app.add_handler(CallbackQueryHandler(button))

    print("Hosting Bot Running 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
