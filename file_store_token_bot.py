import os
import logging
import asyncio
import datetime
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- Config from ENV vars ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
MONGO_URL = os.environ.get("MONGO_URL")
DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "0"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "0"))
FILE_TTL_HOURS = int(os.environ.get("FILE_TTL_HOURS", "12"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", "8080"))

# --- Setup logging ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MongoDB ---
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["file_store_bot"]
files_col = db["files"]
tokens_col = db["tokens"]

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a file and I’ll give you a 24h token link.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Welcome\n/help - Commands\n/get <token> - Get file")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = update.message.effective_attachment

    if not file:
        return await update.message.reply_text("No file detected.")

    file_id = file.file_id
    file_ref = {
        "file_id": file_id,
        "owner": user_id,
        "time": datetime.datetime.utcnow()
    }
    result = files_col.insert_one(file_ref)
    file_db_id = str(result.inserted_id)

    # Generate token
    token = os.urandom(6).hex()
    tokens_col.insert_one({
        "token": token,
        "file_id": file_id,
        "expiry": datetime.datetime.utcnow() + datetime.timedelta(hours=FILE_TTL_HOURS)
    })

    link = f"https://t.me/{context.bot.username}?start={token}"
    await update.message.reply_text(f"✅ File saved! Use this link (valid {FILE_TTL_HOURS}h):\n{link}")

    # Log to channel
    try:
        await context.bot.send_message(LOG_CHANNEL_ID, f"User {user_id} stored file {file_id} with token {token}")
    except Exception as e:
        logger.error(f"Log channel error: {e}")

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        return await update.message.reply_text("Usage: /get <token>")

    token = context.args[0]
    entry = tokens_col.find_one({"token": token})

    if not entry:
        return await update.message.reply_text("❌ Invalid token.")

    if datetime.datetime.utcnow() > entry["expiry"]:
        return await update.message.reply_text("⏰ Token expired.")

    try:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=entry["file_id"])
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to fetch file.")

async def webhook_start():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, save_file))

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(webhook_start())
