# cpy-333
import math
from datetime import datetime
import csv
import json
from abc import ABC, abstractmethod


class InvalidTransactionError(Exception):
    """Exception raised for invalid transaction attributes, such as a zero or negative amount."""
    pass


class Transaction(ABC):
    def __init__(self, city, date, time, amount, status):
        self.city = city
        self.date = date 
        self.time = time
        self.amount = amount
        self.status = status

    @abstractmethod
    def get_net_impact(self) -> float:
        """
        Post-condition: Returns the mathematical net impact of the transaction as a float.
        """

    @property
    def city(self):
        return self._city
        
    @city.setter
    def city(self, value):
        self._city = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not value:
            raise ValueError("Date cannot be empty")
        self._date = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if not value:
            raise ValueError("Time cannot be empty")
        self._time = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        """
        Pre-condition: amount > 0
        """
        parsed_amount = float(value)
        if not math.isfinite(parsed_amount) or parsed_amount <= 0:
            raise InvalidTransactionError("Amount must be a finite number greater than zero")
        self._amount = parsed_amount

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def __str__(self):
        return f"Transaction({self.city}, {self.date}, {self.time}, PKR {self.amount}, {self.status})"


class CreditTransaction(Transaction):
    def __init__(self, city, date, time, amount, status):
        super().__init__(city, date, time, amount, status) 

    def get_net_impact(self) -> float:
        """
        Post-condition: Returns the net impact as a positive float representing an inflow.
        """
        return self.amount


class DebitTransaction(Transaction):
    def __init__(self, city, date, time, amount, status):
        super().__init__(city, date, time, amount, status)

    def get_net_impact(self) -> float:
        """
        Post-condition: Returns the net impact as a negative float representing an outflow.
        """
        return -self.amount


class FileLoader(ABC):
    """Abstract base class for loading and parsing transaction files."""

    def __init__(self):
        self.skipped_count = 0

    @abstractmethod
    def parse_file(self, filepath: str) -> list[Transaction]:
        """
        Parse a file at the given filepath and extract transaction records.

        Subclasses must implement this method and return a list of Transaction
        objects parsed from the specified file.
        """

    def _build_transaction(self, row: dict) -> Transaction:
        """Converts a raw dictionary record into a CreditTransaction or DebitTransaction."""
        if not isinstance(row, dict):
            raise TypeError("Record must be a dictionary")

        tx_type = str(row["Type"]).strip().title()
        city = row["City"]
        date = row["Date"]
        time = row["Time"]
        amount = row["Amount"]
        status = row["Status"]

        if tx_type == "Credit":
            return CreditTransaction(city, date, time, amount, status)
        elif tx_type == "Debit":
            return DebitTransaction(city, date, time, amount, status)
        else:
            raise ValueError(f"Invalid transaction type: {tx_type}")


class CSVLoader(FileLoader):
    """Loads transactions from a CSV file."""

    def parse_file(self, filepath: str) -> list[Transaction]:
        self.skipped_count = 0
        transactions = []

        try:
            with open(filepath, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        tx = self._build_transaction(row)
                        transactions.append(tx)
                    except (ValueError, KeyError, TypeError, InvalidTransactionError):
                        self.skipped_count += 1
                        continue
        except FileNotFoundError:
            return []

        return transactions


class JSONLoader(FileLoader):
    """Loads transactions from a JSON file."""

    def parse_file(self, filepath: str) -> list[Transaction]:
        self.skipped_count = 0
        transactions = []

        try:
            with open(filepath, mode="r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        if not isinstance(data, list):
            return []

        for record in data:
            try:
                tx = self._build_transaction(record)
                transactions.append(tx)
            except (ValueError, KeyError, TypeError, InvalidTransactionError):
                self.skipped_count += 1
                continue

        return transactions


class IngestionQueue:
    """Custom FIFO queue for buffering ingested transactions."""

    def __init__(self):
        self._items = []

    def is_empty(self) -> bool:
        """
        Pre-condition: Queue is initialized.
        Post-condition: Returns True if the queue has no items, False otherwise.
        """
        return len(self._items) == 0

    def enqueue(self, item) -> None:
        """
        Pre-condition: item is a valid object to be queued.
        Post-condition: Appends item to the back of the queue.
        """
        self._items.append(item)

    def dequeue(self):
        """
        Pre-condition: Queue is not empty.
        Post-condition: Removes and returns the oldest item from the front of the queue.
        """
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty queue")
        return self._items.pop(0)

# cpy-333
class FilterHistoryStack:
    """Custom LIFO stack for storing previous filter states."""

    def __init__(self):
        self._items = []

    def is_empty(self) -> bool:
        """
        Pre-condition: Stack is initialized.
        Post-condition: Returns True if the stack has no items, False otherwise.
        """
        return len(self._items) == 0

    def push(self, state) -> None:
        """
        Pre-condition: state is a valid filter state snapshot (e.g., (city, date, tx_type)).
        Post-condition: Pushes state onto the top of the stack.
        """
        self._items.append(state)

    def pop(self):
        """
        Pre-condition: Stack is not empty.
        Post-condition: Removes and returns the most recently pushed filter state from the top of the stack.
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()



class AuditNode:
    """Node in a singly linked list holding a 4-tuple (timestamp, action_type, record_count, net_amount)."""

    def __init__(self, record: tuple):
        self.record = record
        self.next = None


class ExportAuditLinkedList:
    """Custom singly linked list for storing chronological audit trail records."""

    def __init__(self):
        self.head = None

    def append(self, record: tuple) -> None:
        """
        Pre-condition: record is a 4-tuple (timestamp, action_type, record_count, net_amount).
        Post-condition: Appends a new AuditNode containing record to the tail of the linked list.
        """
        new_node = AuditNode(record)
        if self.head is None:
            self.head = new_node
            return

        current = self.head
        while current.next is not None:
            current = current.next
        current.next = new_node

    def get_all_records(self) -> list[tuple]:
        """
        Pre-condition: Linked list is initialized.
        Post-condition: Traverses from head to tail and returns all audit records in insertion order.
        """
        records = []
        current = self.head
        while current is not None:
            records.append(current.record)
            current = current.next
        return records


class FinPayEngine:
    """Core backend engine coordinating ingestion, filtering, state history, and audit logging."""

    def __init__(self):
        self.all_transactions = []
        self.displayed_transactions = []
        self.unique_cities = set()
        self.unique_dates = set()
        self.ingestion_queue = IngestionQueue()
        self.filter_stack = FilterHistoryStack()
        self.audit_log = ExportAuditLinkedList()
        self.current_filter = ("All", "All", "All")

    def load_data(self, filepath: str) -> tuple[int, int]:
        """
        Pre-condition: filepath points to a .csv or .json transaction file.
        Post-condition: Loads valid transactions via IngestionQueue, updates sets, logs LOAD event,
                        and returns (loaded_count, skipped_count).
        """
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext == ".csv":
            loader = CSVLoader()
        elif ext == ".json":
            loader = JSONLoader()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        parsed = loader.parse_file(filepath)

        for tx in parsed:
            self.ingestion_queue.enqueue(tx)

        while not self.ingestion_queue.is_empty():
            self.all_transactions.append(self.ingestion_queue.dequeue())

        self.displayed_transactions = list(self.all_transactions)
        self.current_filter = ("All", "All", "All")

        self.unique_cities.clear()
        self.unique_dates.clear()
        for tx in self.all_transactions:
            self.unique_cities.add(tx.city)
            self.unique_dates.add(tx.date)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_amount = sum(tx.get_net_impact() for tx in parsed)
        self.audit_log.append((timestamp, "LOAD", len(parsed), net_amount))

        return (len(parsed), loader.skipped_count)


    def apply_filters(self, city: str, date: str, tx_type: str) -> list[Transaction]:
        """
        Pre-condition: city, date, and tx_type are valid filter strings (or 'All').
        Post-condition: Pushes previous filter state to stack, filters all_transactions into
                        displayed_transactions, logs FILTER event, and returns displayed_transactions.
        """
        self.filter_stack.push(self.current_filter)
        self.current_filter = (city, date, tx_type)

        filtered = []
        for tx in self.all_transactions:
            city_match = (city == "All" or tx.city == city)
            date_match = (date == "All" or tx.date == date)
            type_match = (
                tx_type == "All"
                or (tx_type == "Credit" and isinstance(tx, CreditTransaction))
                or (tx_type == "Debit" and isinstance(tx, DebitTransaction))
            )
            if city_match and date_match and type_match:
                filtered.append(tx)

        self.displayed_transactions = filtered
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_amount = sum(tx.get_net_impact() for tx in self.displayed_transactions)
        self.audit_log.append((timestamp, "FILTER", len(self.displayed_transactions), net_amount))
        return self.displayed_transactions


    def revert_last_filter(self) -> tuple[str, str, str]:
        if self.filter_stack.is_empty():
            raise IndexError("No previous filter state to revert to")


        prev_city, prev_date, prev_type = self.filter_stack.pop()
        self.current_filter = (prev_city, prev_date, prev_type)
       

        filtered = []
        for tx in self.all_transactions:
            city_match = (prev_city == "All" or tx.city == prev_city)
            date_match = (prev_date == "All" or tx.date == prev_date)
            type_match = (
                prev_type == "All"
                or (prev_type == "Credit" and isinstance(tx, CreditTransaction))
                or (prev_type == "Debit" and isinstance(tx, DebitTransaction))
            )
            if city_match and date_match and type_match:
                filtered.append(tx)

        self.displayed_transactions = filtered


        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_amount = sum(tx.get_net_impact() for tx in self.displayed_transactions)
        self.audit_log.append((timestamp, "REVERT", len(self.displayed_transactions), net_amount))
        return self.current_filter

    def clear_filters(self) -> list[Transaction]:
        """
        Pre-condition: FinPayEngine is initialized.
        Post-condition: Saves active filter if non-default, resets filter to All,
                        restores full transaction list, logs CLEAR event, and returns it.
        """
        if self.current_filter != ("All", "All", "All"):
            self.filter_stack.push(self.current_filter)

        self.current_filter = ("All", "All", "All")
        self.displayed_transactions = list(self.all_transactions)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_amount = sum(tx.get_net_impact() for tx in self.displayed_transactions)
        self.audit_log.append((timestamp, "CLEAR", len(self.displayed_transactions), net_amount))
        return self.displayed_transactions

    def export(self, csv_filepath: str = "exported_transactions.csv", audit_filepath: str = "audit_log.txt") -> None:
        """
        Pre-condition: FinPayEngine is initialized.
        Post-condition: Exports displayed_transactions to CSV with CPY-0000/cpy-333 markers,
                        logs EXPORT event, and writes the full audit linked list to audit_log.txt.
        """
        with open(csv_filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["City", "Date", "Time", "Type", "Amount", "Status"])
            writer.writeheader()

            for tx in self.displayed_transactions:
                tx_type = "Credit" if isinstance(tx, CreditTransaction) else "Debit"
                writer.writerow({
                    "City": tx.city,
                    "Date": tx.date,
                    "Time": tx.time,
                    "Type": tx_type,
                    "Amount": tx.amount,
                    "Status": tx.status,
                })

            writer.writerow({
                "City": "CPY-0000",
                "Date": "",
                "Time": "",
                "Type": "",
                "Amount": "",
                "Status": "cpy-333",
            })

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_amount = sum(tx.get_net_impact() for tx in self.displayed_transactions)
        self.audit_log.append((timestamp, "EXPORT", len(self.displayed_transactions), net_amount))

        with open(audit_filepath, mode="w", encoding="utf-8") as log_file:
            for ts, action, count, net in self.audit_log.get_all_records():
                log_file.write(f"[{ts}] {action} | Records: {count} | Net Impact: PKR {net:.2f}\n")