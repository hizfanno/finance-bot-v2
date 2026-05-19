from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from app.services.transaction_service import add_transaction, get_transactions

# Conversation states
AMOUNT, CATEGORY, DESCRIPTION = range(3)


# =========================
# START MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["➕ Add", "📋 List"],
        ["📊 Summary"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🚀 Finance Bot Ready!\nChoose a menu:",
        reply_markup=reply_markup
    )


# =========================
# ADD FLOW STEP 1
# =========================
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Enter amount:",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT


# =========================
# ADD FLOW STEP 2
# =========================
async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        context.user_data["amount"] = amount

        category_keyboard = [
            ["🍔 Food", "☕ Coffee"],
            ["🚗 Transport", "🛍 Shopping"],
            ["🏠 Needs", "🎉 Entertainment"],
            ["💼 Work", "📦 Misc"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            category_keyboard,
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


# =========================
# ADD FLOW STEP 3
# =========================
async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = (
        update.message.text
        .replace("🍔 ", "")
        .replace("☕ ", "")
        .replace("🚗 ", "")
        .replace("🛍 ", "")
        .replace("🏠 ", "")
        .replace("🎉 ", "")
        .replace("💼 ", "")
        .replace("📦 ", "")
    )

    context.user_data["category"] = category

    await update.message.reply_text(
        "📝 Enter description:",
        reply_markup=ReplyKeyboardRemove()
    )

    return DESCRIPTION


# =========================
# SAVE TRANSACTION
# =========================
async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    amount = context.user_data["amount"]
    category = context.user_data["category"]
    telegram_id = str(update.effective_user.id)

    transaction = add_transaction(
        telegram_id=telegram_id,
        amount=amount,
        category=category,
        description=description
    )

    # Remove old keyboard and show save result
    await update.message.reply_text(
        f"✅ Expense saved!\n\n"
        f"💰 Amount: Rp {transaction.amount:,.0f}\n"
        f"📂 Category: {transaction.category}\n"
        f"📝 Description: {transaction.description}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Show main menu again
    reply_keyboard = [
        ["➕ Add", "📋 List"],
        ["📊 Summary"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🏠 Back to main menu:",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# =========================
# LIST TRANSACTIONS
# =========================
async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    transactions = get_transactions(telegram_id)

    if not transactions:
        await update.message.reply_text("📭 No transactions yet.")
        return

    message = "📋 Recent Transactions:\n\n"

    for trx in transactions[-10:]:
        message += (
            f"💰 Rp {trx.amount:,.0f}\n"
            f"📂 {trx.category}\n"
            f"📝 {trx.description}\n"
            f"────────────\n"
        )

    await update.message.reply_text(message)


# =========================
# BUTTON HANDLER
# =========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "➕ Add":
        return await add_expense_start(update, context)

    elif text == "📋 List":
        await list_expenses(update, context)

    elif text == "📊 Summary":
        await update.message.reply_text(
            "📊 Summary feature coming soon 🚧"
        )

    return ConversationHandler.END