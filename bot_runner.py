from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
import os
from app.bot.handlers import add_expense, list_expenses

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("add", add_expense))
telegram_app.add_handler(CommandHandler("list", list_expenses))


if __name__ == "__main__":
    print("Bot is running...")
    telegram_app.run_polling()