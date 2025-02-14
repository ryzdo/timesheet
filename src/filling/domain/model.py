from datetime import date
from typing import Final

from .enums import EmploymentCode


MAX_DAY_HOURS: Final = 14
MAX_NIGHT_HOURS: Final = 8


class DuplicateCodeError(Exception):
    pass


class InvalidShiftHoursError(Exception):
    pass


class WorkTime:
    def __init__(self, code: EmploymentCode, hours: float) -> None:
        self.code = code
        self.hours = hours
        self._validate_time()

    def _validate_time(self) -> None:
        match self.code:
            case EmploymentCode.DAY_HOUR:
                if not (0 < self.hours <= MAX_DAY_HOURS):
                    raise InvalidShiftHoursError(f"Invalid hours for {self.code._name_}: {self.hours}")
            case EmploymentCode.NIGHT_HOUR:
                if not (0 < self.hours <= MAX_NIGHT_HOURS):
                    raise InvalidShiftHoursError(f"Invalid hours for {self.code._name_}: {self.hours}")
            case _:
                raise InvalidShiftHoursError(f"Unknown employment code: {self.code}")


class WorkDay:
    def __init__(self, date: date) -> None:
        self.date = date
        self._shift: set[WorkTime] = set()

    def add_work_time(self, work_time: WorkTime) -> None:
        if not self.is_code_unique(work_time):
            raise DuplicateCodeError("Cannot add work time: duplicate code")
        self._shift.add(work_time)

    @property
    def total_hours(self) -> float:
        return sum(shift.hours for shift in self._shift)

    def is_code_unique(self, work_time: WorkTime) -> bool:
        return not any(shift.code == work_time.code for shift in self._shift)
