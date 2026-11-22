from backend import (Transaction, 
                     CreditTransaction, 
                     DebitTransaction, 
                     InvalidTransactionError, 
                     FileLoader,
                     CSVLoader,
                     JSONLoader,
                     FilterHistoryStack,
                     IngestionQueue, 
                     ExportAuditLinkedList, 
                     FinPayEngine,
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
json_loader = JSONLoader()
json_txs = json_loader.parse_file("data/Transactions.json")
print(f"JSON Loaded: {len(json_txs)}, Skipped: {json_loader.skipped_count}")

s1= FilterHistoryStack()
s1.push("State A")
s1.push("State B")
s1.push("State C")
while not s1.is_empty():
    print(s1.pop())

# XXXXXXXXXXXXXXXXXXXX -----------------------------  XXXXXXXXXXXXXXXXXXXXXXX
q = IngestionQueue()
for item in ["a", "b", "c"]:
    q.enqueue(item)

while not q.is_empty():
    print("Dequeued:", q.dequeue())

try:
    q.dequeue()
except IndexError as e:
    print(f"Success! Caught IndexError on empty queue: {e}")

# --- ExportAuditLinkedList Tests ---
audit = ExportAuditLinkedList()
print("Empty audit list:", audit.get_all_records())

audit.append(("2026-10-18 09:00:00", "LOAD", 9, 85548.75))
audit.append(("2026-10-18 09:05:00", "FILTER", 3, 12000.0))
audit.append(("2026-10-18 09:10:00", "EXPORT", 3, 12000.0))

records = audit.get_all_records()
print("Audit records count:", len(records))
for rec in records:
    print(" ", rec)

try:
    records[0][0] = "x"
except TypeError as e:
    print(f"Success! Tuple immutability verified: {e}")

# --- FinPayEngine End-to-End Tests ---
engine = FinPayEngine()
loaded, skipped = engine.load_data("data/Transactions.csv")
net_total = sum(tx.get_net_impact() for tx in engine.all_transactions)
print(f"Engine Loaded: {loaded}, Skipped: {skipped}, Net Impact: {net_total}")
print("Unique Cities:", engine.unique_cities)
print("Unique Dates:", engine.unique_dates)

# Test 1: Apply two filters in sequence
engine.apply_filters("Karachi", "All", "All")
print("After Karachi filter:", len(engine.displayed_transactions))

engine.apply_filters("Karachi", "All", "Credit")
print("After Karachi + Credit filter:", len(engine.displayed_transactions))

# Test 2: Revert last filter (should go back to Karachi + All)
restored = engine.revert_last_filter()
print("Reverted to:", restored, "| Count:", len(engine.displayed_transactions))

# Test 3: Clear filters (should return all 9)
engine.clear_filters()
print("After clear_filters:", len(engine.displayed_transactions))

# Test 4: Export CSV + audit_log.txt
engine.export()
print("Exported CSV and audit_log.txt successfully!")