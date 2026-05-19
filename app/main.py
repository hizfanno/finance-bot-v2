from fastapi import FastAPI
from app.database.connection import engine, Base
from app.models.transaction import Transaction
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from app.bot.handlers import (
    start,
    add_expense,
    button_handler,
    list_transactions,
    daily_summary,
    monthly_summary
)
import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI app
app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Health check endpoints
@app.get("/")
def root():
    return {"message": "Finance Bot v2 is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Telegram bot startup
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

telegram_app = Application.builder().token(TOKEN).build()

# Commands
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("add", add_expense))
telegram_app.add_handler(CommandHandler("list", list_transactions))
telegram_app.add_handler(CommandHandler("daily", daily_summary))
telegram_app.add_handler(CommandHandler("monthly", monthly_summary))

# Button handler
telegram_app.add_handler(CallbackQueryHandler(button_handler))


# Run bot when file executed directly
if __name__ == "__main__":
    print("Bot started...")
    telegram_app.run_polling()