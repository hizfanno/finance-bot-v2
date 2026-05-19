from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from app.services.transaction_service import (
    add_transaction,
    get_transactions
)

# Conversation states
AMOUNT, CATEGORY, DESCRIPTION = range(3)


# ------------------------
# Add Expense (Conversation Flow)
# ------------------------

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Enter amount:"
    )
    return AMOUNT


async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        context.user_data["amount"] = amount

        keyboard = [
            ["🍔 Food", "☕ Coffee"],
            ["🚗 Transport", "🛍 Shopping"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            "📂 Select category:",
            reply_markup=reply_markup
        )

        return CATEGORY

    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number."
        )
        return AMOUNT


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text.split(" ", 1)[1]  # remove emoji
    context.user_data["category"] = category

    await update.message.reply_text(
        "📝 Enter description:"
    )

    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    context.user_data["description"] = description

    telegram_id = str(update.effective_user.id)

    transaction = add_transaction(
        telegram_id=telegram_id,
        amount=context.user_data["amount"],
        category=context.user_data["category"],
        description=context.user_data["description"]
    )

    await update.message.reply_text(
        f"✅ Expense saved!\n"
        f"ID: {transaction.id}\n"
        f"Amount: Rp{transaction.amount}\n"
        f"Category: {transaction.category}\n"
        f"Description: {transaction.description}"
    )

    return ConversationHandler.END


# ------------------------
# Old /add manual command
# ------------------------

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
            f"✅ Expense saved!\n"
            f"ID: {transaction.id}\n"
            f"Amount: Rp{transaction.amount}\n"
            f"Category: {transaction.category}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ System error:\n{str(e)}"
        )


# ------------------------
# List Transactions
# ------------------------

async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)

    transactions = get_transactions(telegram_id)

    if not transactions:
        await update.message.reply_text("No transactions found.")
        return

    message = "📋 Transaction List:\n\n"

    for tx in transactions:
        message += (
            f"ID: {tx.id}\n"
            f"Rp{tx.amount} | {tx.category}\n"
            f"{tx.description}\n\n"
        )

    await update.message.reply_text(message)


# ------------------------
# Start Menu
# ------------------------

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
        "🚀 Finance Bot Ready!\nChoose menu:",
        reply_markup=reply_markup
    )


# ------------------------
# Button Menu
# ------------------------

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📋 List":
        await list_expenses(update, context)

    elif text == "📊 Summary":
        await update.message.reply_text(
            "Summary feature coming soon 🚧"
        )