import re

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def format_movie_name(name: str, year: int | None = None) -> str:
    cleaned_name = sanitize_component(name)
    if year is None:
        return cleaned_name
    return f"{cleaned_name} ({year})"


def sanitize_component(value: str) -> str:
    value = _INVALID_CHARS.sub("-", value).strip().rstrip(".")
    if not value:
        raise ValueError("Movie name is empty after filesystem sanitization")
    if value.upper() in _RESERVED_NAMES:
        value = f"_{value}"
    return value
