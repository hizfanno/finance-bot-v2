from app.database.connection import SessionLocal
from app.models.transaction import Transaction
from sqlalchemy import func
from datetime import date


# =========================
# ADD TRANSACTION
# =========================
def add_transaction(telegram_id, amount, category, description):
    db = SessionLocal()

    transaction = Transaction(
        telegram_id=telegram_id,
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
        "total": total,
        "count": count,
        "categories": category_summary
    }