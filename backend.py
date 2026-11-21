# cpy-333
import math
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

    def get_all_records(self) -> list[tuple]:
        """
        Pre-condition: Linked list is initialized.
        Post-condition: Traverses from head to tail and returns all audit records in insertion order.
        """
        records = []
        current = self.head
        while current is not None:
            current.record = records
            current = current.next
            return records


        

    
