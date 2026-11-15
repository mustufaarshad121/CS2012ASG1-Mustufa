from backend import (Transaction, 
                     CreditTransaction, 
                     DebitTransaction, 
                     InvalidTransactionError, 
                     FileLoader,
                     CSVLoader,
                     JSONLOADER,
                     )

try:
    tr = Transaction("Karachi", "2026-10-18", "09:15:00", 100, "Completed")
except TypeError as e:
    print(f"Success! caught typeError: {e}")


try:
    t1 = CreditTransaction("Karachi", "2026-10-18", "09:15:00", 100, "Completed")
    print(t1)
    print(f"Credit Net Impact: {t1.get_net_impact()}")

    t2 = DebitTransaction("Islamabad", "2026-10-20", "11:45:00", 50.5, "Pending")
    print(t2)
    print(f"Debit Net Impact {t2.get_net_impact()}")

    t3 = CreditTransaction("Faislabad", "2026-10-23", "09:30:00", 100, "Pending")
    print(t3)
except InvalidTransactionError as e:
    print(f"Validation error caught successfully: {e}")


try:
    CreditTransaction("Faislabad", "2026-10-24", "10:00:00", 0, "Failed")
except InvalidTransactionError as e:
    print(f"Success! Caught InvalidTransactionError for 0 amount: {e}")

try:
    CreditTransaction("Lahore", "2026-10-25", "10:00:00", -10, "Failed")
except InvalidTransactionError as e:
    print(f"Success! caught Invalid Transaction for -10 amount: {e}")

try:
    CreditTransaction("Islamabad", "2026-10-25", "10:00:00", "abc", "Failed")
except ValueError as e:
    print(f"Sucess! caught Value Error for string: {e}")

#test 7
try:
    t1.amount = -1
except InvalidTransactionError as e:
    print(f"Success! Caught InvalidTransactionError when changing amount to -1: {e}")

t1.status = "Failed"
print(f"Status for T1 is now: {t1.status}")
print(f"Time is still: {t1.time}")


try:
    loader = FileLoader()
except TypeError as e:
    print("Successfully rasied type error", e)


csv_loader = CSVLoader()
csv_txs = csv_loader.parse_file("data/Transactions.csv")
print(f"CSV Loaded: {len(csv_txs)}, Skipped: {csv_loader.skipped_count}")

#JsoN
json_loader = JSONLOADER()
json_txs = json_loader.parse_file("data/Transactions.json")
print(f"JSON Loaded: {len(json_txs)}, Skipped: {json_loader.skipped_count}")

# XXXXXXXXXXXXXXXXXXXX -----------------------------  XXXXXXXXXXXXXXXXXXXXXXX
