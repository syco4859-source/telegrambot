import os
import zipfile
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os
TOKEN = os.getenv("8542846687:AAGxY_wYFouSN5rHHyuK4ZZdX4s3t4b8KHg"
BASE_DIR = "projects"
os.makedirs(BASE_DIR, exist_ok=True)

running_process = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send ZIP file.\n"
        "Bot will auto install requirements.txt\n"
        "Then use /run to start."
    )

async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    file = await update.message.document.get_file()
    zip_path = os.path.join(user_dir, "project.zip")
    await file.download_to_drive(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(user_dir)

    req_file = os.path.join(user_dir, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(["pip3", "install", "-r", req_file])

    await update.message.reply_text("Upload complete & requirements installed.\nUse /run")

async def run_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_dir = os.path.join(BASE_DIR, user_id)
    main_file = os.path.join(user_dir, "main.py")

    if not os.path.exists(main_file):
        await update.message.reply_text("main.py not found!")
        return

    process = subprocess.Popen(
        ["python3", main_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    running_process[user_id] = process
    await update.message.reply_text("Project started 24/7!")

async def stop_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if user_id in running_process:
        running_process[user_id].terminate()
        del running_process[user_id]
        await update.message.reply_text("Project stopped.")
    else:
        await update.message.reply_text("No running project.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("run", run_project))
app.add_handler(CommandHandler("stop", stop_project))
app.add_handler(MessageHandler(filters.Document.FileExtension("zip"), handle_zip))

print("Bot Running...")
app.run_polling()

if __name__ == "__main__":
    main()
