from dataclasses import dataclass
from datetime import date
from typing import Final

from .enums import EmploymentCode


MAX_DAY_HOURS: Final = 14
MAX_NIGHT_HOURS: Final = 8


class DuplicateCodeError(Exception):
    pass


class InvalidShiftHoursError(Exception):
    pass


@dataclass(unsafe_hash=True)
class WorkTime:
    code: EmploymentCode
    hours: float

    def __repr__(self) -> str:
        return f"WorkTime {self.code.name}: {self.hours}"

    def __post_init__(self) -> None:
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

    def __repr__(self) -> str:
        return f"WorkDay {self.date}"

    def __hash__(self) -> int:
        return hash(self.date)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkDay):
            return False
        return other.date == self.date

    def add_work_time(self, work_time: WorkTime) -> None:
        if not self.is_code_unique(work_time):
            raise DuplicateCodeError("Cannot add work time: duplicate code")
        self._shift.add(work_time)

    @property
    def total_hours(self) -> float:
        return sum(shift.hours for shift in self._shift)

    def is_code_unique(self, work_time: WorkTime) -> bool:
        return not any(shift.code == work_time.code for shift in self._shift)
