from telegram import Update
from telegram.ext import ContextTypes

from app.services.transaction_service import (
    add_transaction,
    get_transactions_by_user
)


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # cek jumlah argumen
        if len(context.args) < 3:
            await update.message.reply_text(
                "Format salah.\nContoh:\n/add 50000 Food Makan siang"
            )
            return

        # parsing input
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:])

        telegram_id = str(update.effective_user.id)

        # simpan ke database
        transaction = add_transaction(
            telegram_id=telegram_id,
            amount=amount,
            category=category,
            description=description
        )

        # reply sukses
        await update.message.reply_text(
            f"✅ Transaksi tersimpan!\n"
            f"ID: {transaction.id}\n"
            f"Amount: Rp{transaction.amount}\n"
            f"Category: {transaction.category}\n"
            f"Description: {transaction.description}"
        )

    except IndexError:
        await update.message.reply_text(
            "Format salah.\nContoh:\n/add 50000 Food Makan siang"
        )

    except ValueError:
        await update.message.reply_text(
            "Amount harus angka.\nContoh:\n/add 50000 Food Makan siang"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error sistem:\n{str(e)}"
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