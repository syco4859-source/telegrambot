import os
import zipfile
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

BASE_DIR = "projects"
os.makedirs(BASE_DIR, exist_ok=True)

running_process = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ZIP file bhejo jisme main.py ho.")

async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    file = await update.message.document.get_file()
    zip_path = os.path.join(user_folder, "project.zip")
    await file.download_to_drive(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(user_folder)

    req_path = os.path.join(user_folder, "requirements.txt")
    if os.path.exists(req_path):
        subprocess.run(["pip", "install", "-r", req_path])

    await update.message.reply_text("Upload complete. Use /run")

async def run_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(BASE_DIR, user_id)
    main_file = os.path.join(user_folder, "main.py")

    if not os.path.exists(main_file):
        await update.message.reply_text("main.py not found!")
        return

    process = subprocess.Popen(["python", main_file])
    running_process[user_id] = process

    await update.message.reply_text("Project started!")

async def stop_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if user_id in running_process:
        running_process[user_id].terminate()
        del running_process[user_id]
        await update.message.reply_text("Project stopped.")
    else:
        await update.message.reply_text("No running project.")

def main():
    if not TOKEN:
        print("BOT_TOKEN not found in environment variables")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_project))
    app.add_handler(CommandHandler("stop", stop_project))
    app.add_handler(MessageHandler(filters.Document.FileExtension("zip"), handle_zip))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
