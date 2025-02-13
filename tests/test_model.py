# Максимальное количество часов в день не может привышать 22(24 часа в сутках - 2 часа на обед) из них 8 часов ночные.
# Отработанные часы могут быть дневными и ночными (далее планируется дабавить сверхурочные, отпуск, выходные).
# Каждый вид отработанных часов за один день может быть только один раз (использовать Dict?). При попытке добавления
# часов вид которых уже есть возникает исключение.
# Исключение также возникает при попытке добавления часов, если общая сумма больше 22. Или добавить проверки
import datetime

import pytest

from src.filling.domain.enums import EmploymentCode
from src.filling.domain.model import DuplicateCodeError, EmploymentDay, EmploymentHours


TODAY = datetime.datetime.now(tz=datetime.timezone.utc).date()


def test_employment_hours_validation() -> None:
    # Корректные данные
    EmploymentHours(EmploymentCode.DAY_SHIFT, 8)
    EmploymentHours(EmploymentCode.NIGHT_SHIFT, 6)

    # Некорректные данные
    with pytest.raises(ValueError, match="Invalid hours for DAY_SHIFT: 15"):
        EmploymentHours(EmploymentCode.DAY_SHIFT, 15)

    with pytest.raises(ValueError, match="Invalid hours for NIGHT_SHIFT: -1"):
        EmploymentHours(EmploymentCode.NIGHT_SHIFT, -1)


# Простой тест на добавление разного вида часов в один день.
def test_for_adding_different_types_of_hours_in_one_day() -> None:
    employment_day = EmploymentDay(TODAY)
    hours_day = EmploymentHours(EmploymentCode.DAY_SHIFT, 8)
    hours_night = EmploymentHours(EmploymentCode.NIGHT_SHIFT, 2)
    total = hours_day.hours + hours_night.hours

    employment_day.add_time(hours_day)
    employment_day.add_time(hours_night)

    assert employment_day.total == total


# Тест нельзя добавить 2 записи одного вида часов.
def test_cannot_add_2_records_same_employment_code() -> None:
    employment_day = EmploymentDay(TODAY)
    hours_day = EmploymentHours(EmploymentCode.DAY_SHIFT, 8)
    another_hours_day = EmploymentHours(EmploymentCode.DAY_SHIFT, 3)

    assert employment_day.can_add_time(hours_day)
    employment_day.add_time(hours_day)

    assert employment_day.can_add_time(another_hours_day) is False


# Тест ошибка при попытке добавить 2 записи одного вида часов.
def test_duplicate_employment_code_raises_error() -> None:
    employment_day = EmploymentDay(TODAY)

    hours1 = EmploymentHours(EmploymentCode.DAY_SHIFT, 8)
    hours2 = EmploymentHours(EmploymentCode.DAY_SHIFT, 4)

    employment_day.add_time(hours1)

    with pytest.raises(DuplicateCodeError, match="Cannot add employment hours: duplicate code"):
        employment_day.add_time(hours2)
