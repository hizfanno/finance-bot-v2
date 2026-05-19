from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from app.services.transaction_service import (
    add_transaction,
    get_transactions
)


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:])

        telegram_id = str(update.effective_user.id)

        transaction = add_transaction(
            telegram_id=telegram_id,
            amount=amount,
            category=category,
            description=description
        )

        await update.message.reply_text(
            f"✅ Transaksi tersimpan!\n"
            f"ID: {transaction.id}\n"
            f"Amount: {transaction.amount}\n"
            f"Category: {transaction.category}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error sistem:\n{str(e)}"
        )


async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)

    transactions = get_transactions(telegram_id)

    if not transactions:
        await update.message.reply_text("Belum ada transaksi.")
        return

    message = "📋 Daftar Transaksi:\n\n"

    for tx in transactions:
        message += (
            f"ID: {tx.id}\n"
            f"Rp{tx.amount} | {tx.category}\n"
            f"{tx.description}\n\n"
        )

    await update.message.reply_text(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ Add", "📋 List"],
        ["📊 Summary"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🚀 Finance Bot Ready!\nPilih menu:",
        reply_markup=reply_markup
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "➕ Add":
        await update.message.reply_text(
            "Gunakan format:\n/add 5000 coffee ngopi"
        )

    elif text == "📋 List":
        await list_expenses(update, context)

    elif text == "📊 Summary":
        await update.message.reply_text(
            "Summary feature coming soon 🚧"
        )