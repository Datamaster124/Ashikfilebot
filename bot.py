import os
import json
import uuid
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.environ.get("8457775345:AAHMfsBlJrHTSHomyt3-aZmggUtiI5vxOsw")
ADMIN_ID = int(os.environ.get("1244702812", 0))
USERS_FILE = "users.json"
FILES_FILE = "files.json"

# Load users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = []

# Load files
if os.path.exists(FILES_FILE):
    with open(FILES_FILE, "r") as f:
        files = json.load(f)
else:
    files = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def save_files():
    with open(FILES_FILE, "w") as f:
        json.dump(files, f)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a file and I will generate a unique link.")

def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.video or update.message.audio
    if file:
        file_id = str(uuid.uuid4())
        files[file_id] = file.file_id
        save_files()
        update.message.reply_text(f"File uploaded! Use this link to get it:\n/get {file_id}")
    else:
        update.message.reply_text("Send a valid file (document, audio, video).")

def get_file(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /get <file_id>")
        return
    file_id = context.args[0]
    if file_id in files:
        if update.message.from_user.id not in users:
            users.append(update.message.from_user.id)
            save_users()
        update.message.reply_document(files[file_id])
    else:
        update.message.reply_text("Invalid file link!")

def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("You are not authorized.")
        return
    msg = " ".join(context.args)
    for user_id in users:
        try:
            context.bot.send_message(chat_id=user_id, text=msg)
        except:
            pass
    update.message.reply_text("Broadcast sent!")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get", get_file))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(MessageHandler(Filters.document | Filters.video | Filters.audio, handle_file))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
