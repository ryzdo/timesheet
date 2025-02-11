from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Final


MAX_DAY_HOURS: Final = 14
MAX_NIGHT_HOURS: Final = 8


class EmploymentCode(Enum):
    DAY_SHIFT = (1, "Я", "Продолжительность работы в дневное время")
    NIGHT_SHIFT = (2, "Н", "Продолжительность работы в ночное время")

    def __init__(self, numeric_code: int, letter_code: str, description: str) -> None:
        self.numeric_code = numeric_code
        self.letter_code = letter_code
        self.description = description


@dataclass(unsafe_hash=True)
class EmploymentHours:
    code: EmploymentCode
    hours: float


class EmploymentDay:
    def __init__(self, date: date) -> None:
        self.date = date
        self._employment_hours: set[EmploymentHours] = set()

    def add_time(self, employment_hours: EmploymentHours) -> None:
        self._employment_hours.add(employment_hours)

    @property
    def total(self) -> float:
        return sum(employment_hours.hours for employment_hours in self._employment_hours)

    def can_add_time(self, employment_hours: EmploymentHours) -> bool:
        return (employment_hours.code is EmploymentCode.DAY_SHIFT and 0 < employment_hours.hours <= MAX_DAY_HOURS) or (
            employment_hours.code is EmploymentCode.NIGHT_SHIFT and 0 < employment_hours.hours <= MAX_NIGHT_HOURS
        )
