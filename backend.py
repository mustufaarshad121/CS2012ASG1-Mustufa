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
        # --- EDITED: Added math.isfinite() to block "nan" and "inf" from sneaking past the check ---
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
        # --- EDITED: Changed the word 'positive' to 'negative' to match the -self.amount math ---
        Post-condition: Returns the net impact as a negative float representing an outflow.
        """
        return -self.amount


class FileLoader(ABC):
    """Abstraction base class for loading adn parsing trasnaction file"""


    def __init__(self):
        self.skipped_count = 0

    @abstractmethod
    def parse_file(self, filepath: str) -> list[Transaction]:
        """
        Parse a file at the given filepath and extract transaction records.

        Subclasses must implement this method and return a list of Transaction
        objects parsed from the specified file.
        """

