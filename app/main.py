from fastapi import FastAPI
from pydantic import BaseModel
from telegram.ext import Application
from telegram.ext import CommandHandler
from app.bot.handlers import add_expense

app = FastAPI()


# temporary storage
transactions = []


class Transaction(BaseModel):
    amount: int
    category: str
    note: str


@app.get("/")
def root():
    return {"message": "Finance Bot v2 is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/transaction")
def create_transaction(data: Transaction):

    transactions.append(data.model_dump())

    return {
        "status": "success",
        "data": data
    }

@app.put("/transaction/{index}")
def update_transaction(index: int, data: Transaction):

    if index >= len(transactions):
        return {"error": "transaction not found"}

    transactions[index] = data.model_dump()

    return {
        "status": "updated",
        "data": transactions[index]
    }

@app.delete("/transaction/{index}")
def delete_transaction(index: int):

    if index >= len(transactions):
        return {"error": "transaction not found"}

    deleted_data = transactions.pop(index)

    return {
        "status": "deleted",
        "data": deleted_data
    }


@app.get("/transactions")
def get_transactions():

    return {
        "total": len(transactions),
        "data": transactions
    }