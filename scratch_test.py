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
print(f"1. Loaded: {loaded}, Skipped: {skipped}, Net: {net_total}, Cities ({len(engine.unique_cities)}): {engine.unique_cities}")

# 2. Filter by city Karachi -> 2 rows
karachi_rows = engine.apply_filters("Karachi", "All", "All")
print(f"2. Karachi rows: {len(karachi_rows)}")

# 3. Apply second filter, then revert -> back on Karachi list (2 rows)
engine.apply_filters("Karachi", "All", "Credit")
reverted_filter = engine.revert_last_filter()
print(f"3. Reverted filter: {reverted_filter}, Rows: {len(engine.displayed_transactions)}")

# 4. Revert until empty stack -> clean IndexError, no crash
engine.revert_last_filter()  # pops ("All", "All", "All")
try:
    engine.revert_last_filter()
except IndexError as e:
    print(f"4. Empty stack revert caught cleanly: {e}")

# 5. Clear, then export -> check both output files
engine.apply_filters("Lahore", "All", "All")
engine.clear_filters()
csv_out, log_out = engine.export()
print(f"5. Exported to:\n   {csv_out}\n   {log_out}")

# 6. Missing file and .txt file -> clear errors, no crash
for bad_path in ["data/does_not_exist.csv", "data/notes.txt"]:
    try:
        engine.load_data(bad_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"6. Caught expected error for {bad_path}: {e}")