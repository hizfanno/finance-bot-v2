from app.database.connection import engine
from app.models.base import Base
from app.models.transaction import Transaction

from app.models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created!")


if __name__ == "__main__":
    init_db()