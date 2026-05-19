from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os

load_dotenv()

from app.services.transaction_service import (
    add_transaction,
    get_transactions,
    get_daily_summary,
    get_monthly_summary,
    export_all_transactions_to_csv,
    export_current_month_to_csv
)

# =========================
# AUTH
# =========================
raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [str(x).strip() for x in raw_users.split(",") if x]


def is_authorized(update):
    user_id = str(update.effective_user.id)
    return user_id in ALLOWED_USERS


async def reject_user(update):
    await update.message.reply_text("⛔ Unauthorized access.")


# =========================
# STATES
# =========================
AMOUNT, CATEGORY, DESCRIPTION = range(3)


# =========================
# MAIN MENU
# =========================
def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            ["➕ Add", "📋 List"],
            ["📊 Summary", "📤 Export"],
        ],
        resize_keyboard=True
    )


# =========================
# SUMMARY MENU
# =========================
def get_summary_menu():
    return ReplyKeyboardMarkup(
        [
            ["📅 Today", "📆 This Month"],
            ["🏠 Back"]
        ],
        resize_keyboard=True
    )


# =========================
# EXPORT MENU
# =========================
def get_export_menu():
    return ReplyKeyboardMarkup(
        [
            ["📅 Current Month", "📂 All Data"],
            ["🏠 Back"]
        ],
        resize_keyboard=True
    )


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    await update.message.reply_text(
        "🚀 Finance Bot Ready!\nChoose a menu:",
        reply_markup=get_main_menu()
    )


# =========================
# ADD FLOW
# =========================
async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    await update.message.reply_text(
        "💰 Enter amount:",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT


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
        f"📝 Description: {transaction.description}"
    )

    await update.message.reply_text(
        "🏠 Back to main menu:",
        reply_markup=get_main_menu()
    )

    return ConversationHandler.END


# =========================
# LIST
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

    for trx in transactions[:10]:
        message += (
            f"👤 {trx.username}\n"
            f"💰 Rp {trx.amount:,.0f}\n"
            f"📂 {trx.category}\n"
            f"📝 {trx.description}\n"
            f"📅 {trx.created_at.strftime('%d-%m-%Y %H:%M')}\n"
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
            f"📅 No transactions on {summary['date']}",
            reply_markup=get_summary_menu()
        )
        return

    message = (
        f"📅 Daily Summary ({summary['date']})\n\n"
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
            f"📆 No transactions in {summary['month']} {summary['year']}",
            reply_markup=get_summary_menu()
        )
        return

    message = (
        f"📆 {summary['month']} {summary['year']} Summary\n\n"
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
# EXPORTS
# =========================
async def export_current_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    telegram_id = str(update.effective_user.id)
    filename = export_current_month_to_csv(telegram_id)

    with open(filename, "rb") as file:
        await update.message.reply_document(
            document=file,
            filename=filename,
            caption="📤 Current month CSV ready!"
        )

    os.remove(filename)


async def export_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject_user(update)

    telegram_id = str(update.effective_user.id)
    filename = export_all_transactions_to_csv(telegram_id)

    with open(filename, "rb") as file:
        await update.message.reply_document(
            document=file,
            filename=filename,
            caption="📤 Full transaction CSV ready!"
        )

    os.remove(filename)


# =========================
# MENU HANDLER
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

    elif text == "📅 Today":
        await daily_summary(update, context)

    elif text == "📆 This Month":
        await monthly_summary(update, context)

    elif text == "📤 Export":
        await update.message.reply_text(
            "📤 Choose export type:",
            reply_markup=get_export_menu()
        )

    elif text == "📅 Current Month":
        await export_current_month(update, context)

    elif text == "📂 All Data":
        await export_all(update, context)

    elif text == "🏠 Back":
        await update.message.reply_text(
            "🏠 Back to main menu:",
            reply_markup=get_main_menu()
        )

    return ConversationHandler.END