from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Base didefinisikan di sini — semua model import dari sini
Base = declarative_base()

# Ambil DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL RAW =", repr(DATABASE_URL))

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing!")

# Fix prefix Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Panggil ini di bot_runner.py untuk create tabel"""
    from app.models.transaction import Transaction  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("Tables created!")


def check_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("DB SUCCESS CONNECTED!")
        return True
    except Exception as e:
        print("DB ERROR:", e)
        return False