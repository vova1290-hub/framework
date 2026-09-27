"""Вспомогательные функции безопасного пользовательского ввода."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить целое число, повторяя ввод при ошибке."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(prompt: str) -> float:
    """Запросить дробное число, повторяя ввод при ошибке."""
    while True:
        try:
            value = input(prompt).replace(",", ".")
            return float(value)
        except ValueError:
            print("Ошибка: введите число.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ДД.ММ.ГГГГ."""
    while True:
        try:
            value = input(prompt)
            return datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            print("Ошибка: используйте формат ДД.ММ.ГГГГ.")


def input_non_empty(prompt: str) -> str:
    """Запросить непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: значение не может быть пустым.")
