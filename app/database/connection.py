from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Base dulu
Base = declarative_base()

# Ambil DATABASE_URL dari Railway
DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL RAW =", repr(DATABASE_URL))

# Validasi kalau kosong
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing!")

# SQLAlchemy Railway fix
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )

# Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Import model setelah Base dibuat
from app.models.transaction import Transaction

# Auto create tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Test connection
try:
    conn = engine.connect()
    print("DB SUCCESS CONNECTED!")
    conn.close()
except Exception as e:
    print("DB ERROR:", e)
    raise