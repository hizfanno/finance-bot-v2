from telegram import Update
from telegram.ext import ContextTypes

from app.services.transaction_service import (
    add_transaction,
    get_transactions_by_user
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

    except Exception:
        await update.message.reply_text(
            "Format salah.\nContoh:\n/add 50000 Food Makan siang"
        )


async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)

    transactions = get_transactions_by_user(telegram_id)

    if not transactions:
        await update.message.reply_text("Belum ada transaksi.")
        return

    message = "Daftar transaksi:\n"

    for trx in transactions:
        message += f"- {trx.category}: Rp{trx.amount} ({trx.description})\n"

    await update.message.reply_text(message)