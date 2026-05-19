from app.services.transaction_service import add_transaction, get_transactions

# test insert
new_tx = add_transaction(
    telegram_id="999999",
    amount=25000,
    category="Transport",
    description="Naik gojek"
)

print("Inserted:", new_tx.id, new_tx.amount)

# test read
transactions = get_transactions("999999")

for t in transactions:
    print(t.id, t.amount, t.category, t.description)