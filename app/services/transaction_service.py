from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.transaction import Transaction


def add_transaction(telegram_id, amount, category, description=None):
    db: Session = SessionLocal()

    try:
        new_transaction = Transaction(
            telegram_id=telegram_id,
            amount=amount,
            category=category,
            description=description
        )

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return new_transaction

    finally:
        db.close()


def get_transactions(telegram_id):
    db: Session = SessionLocal()

    try:
        return db.query(Transaction).filter(
            Transaction.telegram_id == telegram_id
        ).all()

    finally:
        db.close()


def get_transactions_by_user(telegram_id):
    db: Session = SessionLocal()

    try:
        return db.query(Transaction).filter(
            Transaction.telegram_id == telegram_id
        ).all()

    finally:
        db.close()  