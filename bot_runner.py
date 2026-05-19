# =========================
# URUTAN IMPORT PENTING!
# =========================
from dotenv import load_dotenv
load_dotenv()  # 1. Load .env PERTAMA

import os
from app.database.connection import init_db, check_connection
init_db()       # 2. Buat tabel
check_connection()  # 3. Cek koneksi

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from app.bot.handlers import (
    start,
    add_expense_start,
    get_amount,
    get_category,
    get_description,
    list_expenses,
    menu_handler,
    AMOUNT,
    CATEGORY,
    DESCRIPTION
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

telegram_app = Application.builder().token(BOT_TOKEN).build()

# =========================
# Conversation Handler
# =========================
conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^➕ Add$"), add_expense_start)
    ],
    states={
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
    },
    fallbacks=[CommandHandler("start", start)]
)

# =========================
# Register handlers
# =========================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("list", list_expenses))
telegram_app.add_handler(conv_handler)
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

# =========================
# Run bot
# =========================
if __name__ == "__main__":
    print("Bot is running...")
    telegram_app.run_polling()