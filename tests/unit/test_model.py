# Максимальное количество часов в день не может привышать 22(24 часа в сутках - 2 часа на обед) из них 8 часов ночные.
# Отработанные часы могут быть дневными и ночными (далее планируется дабавить сверхурочные, отпуск, выходные).
# Каждый вид отработанных часов за один день может быть только один раз (использовать Dict?). При попытке добавления
# часов вид которых уже есть возникает исключение.
# Исключение также возникает при попытке добавления часов, если общая сумма больше 22. Или добавить проверки
import datetime

import pytest

from src.filling.domain.enums import EmploymentCode
from src.filling.domain.model import DuplicateCodeError, InvalidShiftHoursError, WorkDay, WorkTime


TODAY = datetime.datetime.now(tz=datetime.timezone.utc).date()


def test_work_time_validation() -> None:
    # Корректные данные
    WorkTime(EmploymentCode.DAY_HOUR, 8)
    WorkTime(EmploymentCode.NIGHT_HOUR, 6)

    # Некорректные данные
    with pytest.raises(InvalidShiftHoursError, match="Invalid hours for DAY_HOUR: 15"):
        WorkTime(EmploymentCode.DAY_HOUR, 15)

    with pytest.raises(InvalidShiftHoursError, match="Invalid hours for NIGHT_HOUR: -1"):
        WorkTime(EmploymentCode.NIGHT_HOUR, -1)


# Простой тест на добавление разного вида рабочего времени в один день.
def test_for_adding_different_types_of_hours_in_one_day() -> None:
    work_day = WorkDay(TODAY)
    day_time = WorkTime(EmploymentCode.DAY_HOUR, 8)
    night_time = WorkTime(EmploymentCode.NIGHT_HOUR, 2)
    total = day_time.hours + night_time.hours

    work_day.add_work_time(day_time)
    work_day.add_work_time(night_time)

    assert work_day.total_hours == total


# Тест нельзя добавить 2 записи одного вида рабочего времени.
def test_cannot_add_2_records_same_employment_code() -> None:
    work_day = WorkDay(TODAY)
    daytime = WorkTime(EmploymentCode.DAY_HOUR, 8)
    another_daytime = WorkTime(EmploymentCode.DAY_HOUR, 3)

    assert work_day.is_code_unique(daytime)
    work_day.add_work_time(daytime)

    assert work_day.is_code_unique(another_daytime) is False


# Тест ошибка при попытке добавить 2 записи одного вида рабочего времени.
def test_duplicate_employment_code_raises_error() -> None:
    work_day = WorkDay(TODAY)

    time1 = WorkTime(EmploymentCode.DAY_HOUR, 8)
    time2 = WorkTime(EmploymentCode.DAY_HOUR, 4)

    work_day.add_work_time(time1)

    with pytest.raises(DuplicateCodeError, match="Cannot add work time: duplicate code"):
        work_day.add_work_time(time2)
