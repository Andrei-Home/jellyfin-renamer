import pytest

from jellyfin_renamer.naming import format_movie_name, sanitize_component


def test_formats_name_with_year() -> None:
    assert format_movie_name("Little Asians Vol. 9", 2023) == "Little Asians Vol. 9 (2023)"


def test_omits_missing_year() -> None:
    assert format_movie_name("Example Movie") == "Example Movie"


def test_sanitizes_filesystem_characters() -> None:
    assert sanitize_component("A: Movie? / Test") == "A- Movie- - Test"


def test_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        sanitize_component("...")


def test_prefixes_reserved_name() -> None:
    assert sanitize_component("CON") == "_CON"
