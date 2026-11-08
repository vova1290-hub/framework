"""Формирование латинских адресов клиентов."""

from django.utils.text import slugify

RUSSIAN = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    (
        "a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y",
        "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f",
        "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya",
    ),
))


def client_slug(name, suffix):
    """Собрать короткий slug с уникальным суффиксом."""
    latin = "".join(RUSSIAN.get(char, char) for char in name.lower())
    base = slugify(latin)[:50].rstrip("-") or "client"
    return f"{base}-{suffix}"
