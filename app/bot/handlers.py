from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os

load_dotenv()

from app.services.transaction_service import (
    add_transaction,
    get_transactions,
    get_daily_summary,
    get_monthly_summary
)

# =========================
# AUTH
# =========================
ALLOWED_USERS = [
    str(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x
]


def is_authorized(update):
    user_id = str(update.effective_user.id)
    return user_id in ALLOWED_USERS


async def reject_user(update):
    await update.message.reply_text("⛔ Unauthorized access.")


# =========================
# Conversation states
# =========================
AMOUNT, CATEGORY, DESCRIPTION = range(3)


# =========================
# MAIN MENU
# =========================
def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            ["➕ Add", "📋 List"],
            ["📊 Summary"]
        ],
        resize_keyboard=True
    )


# =========================
# SUMMARY MENU
# =========================
def get_summary_menu():
    return ReplyKeyboardMarkup(
        [
            ["📅 Daily", "📆 Monthly"],
            ["🏠 Back"]
        ],
        resize_keyboard=True
    )


# =========================
# START MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    await update.message.reply_text(
        "🚀 Finance Bot Ready!\nChoose a menu:",
        reply_markup=get_main_menu()
    )


# =========================
# ADD FLOW STEP 1
# =========================
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    await update.message.reply_text(
        "💰 Enter amount:",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT


# =========================
# ADD FLOW STEP 2
# =========================
async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

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
        await update.message.reply_text("❌ Please enter a valid number.")
        return AMOUNT


# =========================
# ADD FLOW STEP 3
# =========================
async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

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
    if not is_authorized(update):
        return await reject_user(update)

    description = update.message.text
    amount = context.user_data["amount"]
    category = context.user_data["category"]

    user = update.effective_user
    telegram_id = str(user.id)
    username = user.username or user.first_name

    transaction = add_transaction(
        telegram_id=telegram_id,
        username=username,
        amount=amount,
        category=category,
        description=description
    )

    await update.message.reply_text(
        f"✅ Expense saved!\n\n"
        f"💰 Amount: Rp {transaction.amount:,.0f}\n"
        f"📂 Category: {transaction.category}\n"
        f"📝 Description: {transaction.description}",
        reply_markup=ReplyKeyboardRemove()
    )

    await update.message.reply_text(
        "🏠 Back to main menu:",
        reply_markup=get_main_menu()
    )

    return ConversationHandler.END


# =========================
# LIST TRANSACTIONS
# =========================
async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    telegram_id = str(update.effective_user.id)
    transactions = get_transactions(telegram_id)

    if not transactions:
        await update.message.reply_text(
            "📭 No transactions yet.",
            reply_markup=get_main_menu()
        )
        return

    message = "📋 Recent Transactions:\n\n"

    for trx in transactions[-10:]:
        message += (
            f"👤 {trx.username}\n"
            f"💰 Rp {trx.amount:,.0f}\n"
            f"📂 {trx.category}\n"
            f"📝 {trx.description}\n"
            f"────────────\n"
        )

    await update.message.reply_text(
        message,
        reply_markup=get_main_menu()
    )


# =========================
# DAILY SUMMARY
# =========================
async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    telegram_id = str(update.effective_user.id)
    summary = get_daily_summary(telegram_id)

    if summary["count"] == 0:
        await update.message.reply_text(
            "📅 No transactions today.",
            reply_markup=get_summary_menu()
        )
        return

    message = (
        f"📅 Today Summary\n\n"
        f"💰 Total: Rp {summary['total']:,.0f}\n"
        f"🧾 Transactions: {summary['count']}\n\n"
        f"Breakdown:\n"
    )

    for category, amount in summary["categories"]:
        message += f"• {category}: Rp {amount:,.0f}\n"

    await update.message.reply_text(
        message,
        reply_markup=get_summary_menu()
    )


# =========================
# MONTHLY SUMMARY
# =========================
async def monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    telegram_id = str(update.effective_user.id)
    summary = get_monthly_summary(telegram_id)

    if summary["count"] == 0:
        await update.message.reply_text(
            "📆 No transactions this month.",
            reply_markup=get_summary_menu()
        )
        return

    message = (
        f"📆 This Month Summary\n\n"
        f"💰 Total: Rp {summary['total']:,.0f}\n"
        f"🧾 Transactions: {summary['count']}\n\n"
        f"Breakdown:\n"
    )

    for category, amount in summary["categories"]:
        message += f"• {category}: Rp {amount:,.0f}\n"

    await update.message.reply_text(
        message,
        reply_markup=get_summary_menu()
    )


# =========================
# BUTTON HANDLER
# =========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    text = update.message.text

    if text == "➕ Add":
        return await add_expense_start(update, context)

    elif text == "📋 List":
        await list_expenses(update, context)

    elif text == "📊 Summary":
        await update.message.reply_text(
            "📊 Choose summary type:",
            reply_markup=get_summary_menu()
        )

    elif text == "📅 Daily":
        await daily_summary(update, context)

    elif text == "📆 Monthly":
        await monthly_summary(update, context)

    elif text == "🏠 Back":
        await update.message.reply_text(
            "🏠 Back to main menu:",
            reply_markup=get_main_menu()
        )

    return ConversationHandler.END