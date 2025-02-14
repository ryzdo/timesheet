from enum import Enum


class EmploymentCode(Enum):
    DAY_HOUR = (1, "Я", "Продолжительность работы в дневное время")
    NIGHT_HOUR = (2, "Н", "Продолжительность работы в ночное время")
    VACATION = (9, "ОТ", "Ежегодный основной оплачиваемый отпуск")

    def __init__(self, numeric_code: int, letter_code: str, description: str) -> None:
        self.numeric_code = numeric_code
        self.letter_code = letter_code
        self.description = description
