import json
from collections.abc import Iterator
from urllib.parse import parse_qs, urlparse

import pytest

from jellyfin_renamer.client import JellyfinClient, JellyfinResponseError


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def fake_opener(responses: list[object], urls: list[str]):
    response_iterator: Iterator[object] = iter(responses)

    def opener(request: object, timeout: float, context: object) -> FakeResponse:
        urls.append(request.full_url)
        return FakeResponse(next(response_iterator))

    return opener


def test_selects_exact_movie_library() -> None:
    urls: list[str] = []
    client = JellyfinClient(
        "https://jellyfin.example",
        "secret",
        opener=fake_opener(
            [[{"Name": "Movies", "ItemId": "1", "CollectionType": "movies"}]], urls
        ),
    )

    library = client.select_movie_library("Movies")

    assert library.name == "Movies"
    assert "Library/VirtualFolders" in urls[0]


def test_rejects_non_movie_library() -> None:
    client = JellyfinClient(
        "https://jellyfin.example",
        "secret",
        opener=fake_opener(
            [[{"Name": "TV", "ItemId": "1", "CollectionType": "tvshows"}]], []
        ),
    )

    with pytest.raises(JellyfinResponseError, match="not a movie library"):
        client.select_movie_library("TV")


def test_fetches_paginated_movies() -> None:
    urls: list[str] = []
    client = JellyfinClient(
        "https://jellyfin.example",
        "secret",
        page_size=1,
        opener=fake_opener(
            [
                {"Items": [{"Id": "a", "Name": "A", "Path": "/a.mkv", "ProductionYear": 2020}], "TotalRecordCount": 2},
                {"Items": [{"Id": "b", "Name": "B", "Path": "/b.mkv"}], "TotalRecordCount": 2},
            ],
            urls,
        ),
    )

    movies = list(client.movies("library"))

    assert [movie.id for movie in movies] == ["a", "b"]
    assert parse_qs(urlparse(urls[1]).query)["StartIndex"] == ["1"]
