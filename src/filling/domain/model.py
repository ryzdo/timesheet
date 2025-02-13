from datetime import date
from typing import Final

from .enums import EmploymentCode


MAX_DAY_HOURS: Final = 14
MAX_NIGHT_HOURS: Final = 8


class DuplicateCodeError(Exception):
    pass


class EmploymentHours:
    def __init__(self, code: EmploymentCode, hours: float) -> None:
        self.code = code
        self.hours = hours
        self._validate_hours()

    def _validate_hours(self) -> None:
        """Проверяет, что количество часов допустимо для данного кода смены."""
        match self.code:
            case EmploymentCode.DAY_SHIFT:
                if not (0 < self.hours <= MAX_DAY_HOURS):
                    raise ValueError(f"Invalid hours for DAY_SHIFT: {self.hours}")
            case EmploymentCode.NIGHT_SHIFT:
                if not (0 < self.hours <= MAX_NIGHT_HOURS):
                    raise ValueError(f"Invalid hours for NIGHT_SHIFT: {self.hours}")
            case _:
                raise ValueError(f"Unknown employment code: {self.code}")


class EmploymentDay:
    def __init__(self, date: date) -> None:
        self.date = date
        self._employment_hours: set[EmploymentHours] = set()

    def add_time(self, employment_hours: EmploymentHours) -> None:
        if not self.can_add_time(employment_hours):
            raise DuplicateCodeError("Cannot add employment hours: duplicate code")
        self._employment_hours.add(employment_hours)

    @property
    def total(self) -> float:
        return sum(employment_hours.hours for employment_hours in self._employment_hours)

    def can_add_time(self, employment_hours: EmploymentHours) -> bool:
        return not any(eh.code == employment_hours.code for eh in self._employment_hours)
