# cpy-333
ffrom abc import ABC, abstractmethod

class Transaction(ABC):
    def __init__(self, city, date, time, amount, status):
        self._city = city
        self._date = date 
        self._time = time
        self._amount = amount
        self._status = status

    @abstractmethod
    def get_net_impact(self) -> float:
        pass

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
        if not value & value < 0:
            raise ValueError("Date cannot be empty or date should be greater than zero")
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
        if value < 0:
            raise ValueError("Value cannot be zero or negative")
        self._amount = value
    

    @property
    def status(self):
        return self._status

    @time.setter
    def time(self, value):
        self._status = value

    def __str__(self):
        return f"Transaction({self.city}, {self.date}, {self.time}, ${self.amount}, {self.status})"


t1 = Transaction("Karachi", "2026-10-18", "09:15:00", 100, "Completed")
print(t1)