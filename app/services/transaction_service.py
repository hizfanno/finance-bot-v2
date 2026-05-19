from app.database.connection import SessionLocal
from app.models.transaction import Transaction
from sqlalchemy import func
from datetime import date
import csv
import calendar


# =========================
# ADD TRANSACTION
# =========================
def add_transaction(telegram_id, username, amount, category, description):
    db = SessionLocal()

    transaction = Transaction(
        telegram_id=telegram_id,
        username=username,
        amount=amount,
        category=category,
        description=description
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.close()

    return transaction


# =========================
# GET ALL TRANSACTIONS
# =========================
def get_transactions(telegram_id):
    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.telegram_id == telegram_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    db.close()
    return transactions


# =========================
# DAILY SUMMARY
# =========================
def get_daily_summary(telegram_id):
    db = SessionLocal()

    today = date.today()

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.telegram_id == telegram_id,
            func.date(Transaction.created_at) == today
        )
        .all()
    )

    total = sum(trx.amount for trx in transactions)
    count = len(transactions)

    category_summary = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount)
        )
        .filter(
            Transaction.telegram_id == telegram_id,
            func.date(Transaction.created_at) == today
        )
        .group_by(Transaction.category)
        .all()
    )

    db.close()

    return {
        "date": today.strftime("%d %B %Y"),
        "total": total,
        "count": count,
        "categories": category_summary
    }


# =========================
# MONTHLY SUMMARY
# =========================
def get_monthly_summary(telegram_id):
    db = SessionLocal()

    today = date.today()
    month_name = calendar.month_name[today.month]

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.telegram_id == telegram_id,
            func.extract("month", Transaction.created_at) == today.month,
            func.extract("year", Transaction.created_at) == today.year
        )
        .all()
    )

    total = sum(trx.amount for trx in transactions)
    count = len(transactions)

    category_summary = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount)
        )
        .filter(
            Transaction.telegram_id == telegram_id,
            func.extract("month", Transaction.created_at) == today.month,
            func.extract("year", Transaction.created_at) == today.year
        )
        .group_by(Transaction.category)
        .all()
    )

    db.close()

    return {
        "month": month_name,
        "year": today.year,
        "total": total,
        "count": count,
        "categories": category_summary
    }


# =========================
# EXPORT ALL DATA
# =========================
def export_all_transactions_to_csv(telegram_id):
    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.telegram_id == telegram_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    filename = "transactions_all.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Username",
            "Amount",
            "Category",
            "Description",
            "Created At"
        ])

        for trx in transactions:
            writer.writerow([
                trx.id,
                trx.username,
                trx.amount,
                trx.category,
                trx.description,
                trx.created_at.strftime("%d-%m-%Y %H:%M:%S")
            ])

    db.close()
    return filename


# =========================
# EXPORT CURRENT MONTH
# =========================
def export_current_month_to_csv(telegram_id):
    db = SessionLocal()

    today = date.today()
    month_name = calendar.month_name[today.month]

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.telegram_id == telegram_id,
            func.extract("month", Transaction.created_at) == today.month,
            func.extract("year", Transaction.created_at) == today.year
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )

    filename = f"transactions_{month_name}_{today.year}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Username",
            "Amount",
            "Category",
            "Description",
            "Created At"
        ])

        for trx in transactions:
            writer.writerow([
                trx.id,
                trx.username,
                trx.amount,
                trx.category,
                trx.description,
                trx.created_at.strftime("%d-%m-%Y %H:%M:%S")
            ])

    db.close()
    return filename