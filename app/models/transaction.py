from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)