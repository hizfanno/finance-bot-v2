from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    amount = Column(Numeric, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())