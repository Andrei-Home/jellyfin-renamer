import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import JellyfinLibrary, JellyfinMovie


class JellyfinError(RuntimeError):
    """Base error for Jellyfin API failures."""


class JellyfinConnectionError(JellyfinError):
    """Raised when Jellyfin cannot be reached or returns invalid JSON."""


class JellyfinResponseError(JellyfinError):
    """Raised when Jellyfin returns an unexpected response."""


@dataclass(frozen=True)
class JellyfinClient:
    base_url: str
    api_key: str
    timeout: float = 30.0
    verify_tls: bool = True
    opener: Callable[..., object] = urlopen
    page_size: int = 100

    def _request(self, path: str, params: dict[str, str | int], method: str = "GET") -> bytes:
        query = urlencode(params)
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"
        request = Request(
            url,
            method=method,
            headers={
                "Accept": "application/json",
                "Authorization": f'MediaBrowser Token="{self.api_key}"',
                "User-Agent": "jellyfin-renamer/0.1",
            },
        )
        try:
            with self.opener(request, timeout=self.timeout, context=self._ssl_context()) as response:
                return response.read()
        except HTTPError as error:
            if error.code in (401, 403):
                raise JellyfinResponseError("Jellyfin rejected the API key") from error
            raise JellyfinResponseError(f"Jellyfin returned HTTP {error.code}") from error
        except (URLError, OSError) as error:
            raise JellyfinConnectionError(f"Could not connect to Jellyfin: {error}") from error

    def _request_json(self, path: str, params: dict[str, str | int]) -> object:
        try:
            return json.loads(self._request(path, params))
        except (TypeError, json.JSONDecodeError) as error:
            raise JellyfinConnectionError("Jellyfin returned invalid JSON") from error

    def refresh_library(self) -> None:
        self._request("Library/Refresh", {}, method="POST")

    def _ssl_context(self):
        if self.verify_tls:
            return None
        import ssl

        return ssl._create_unverified_context()

    def libraries(self) -> list[JellyfinLibrary]:
        payload = self._request_json("Library/VirtualFolders", {})
        if not isinstance(payload, list):
            raise JellyfinResponseError("Jellyfin library response was not a list")
        libraries: list[JellyfinLibrary] = []
        for item in payload:
            if not isinstance(item, dict) or not item.get("ItemId") or not item.get("Name"):
                raise JellyfinResponseError("Jellyfin library response contained an invalid item")
            libraries.append(
                JellyfinLibrary(
                    id=str(item["ItemId"]),
                    name=str(item["Name"]),
                    collection_type=item.get("CollectionType"),
                )
            )
        return libraries

    def select_movie_library(self, name: str) -> JellyfinLibrary:
        matches = [library for library in self.libraries() if library.name == name]
        if not matches:
            raise JellyfinResponseError(f"No Jellyfin library named {name!r} was found")
        if len(matches) > 1:
            raise JellyfinResponseError(f"More than one Jellyfin library is named {name!r}")
        library = matches[0]
        if library.collection_type != "movies":
            raise JellyfinResponseError(f"Jellyfin library {name!r} is not a movie library")
        return library

    def movies(self, library_id: str) -> Iterator[JellyfinMovie]:
        start_index = 0
        while True:
            payload = self._request_json(
                "Items",
                {
                    "ParentId": library_id,
                    "Recursive": "true",
                    "IncludeItemTypes": "Movie",
                    "Fields": "Path,ProductionYear",
                    "StartIndex": start_index,
                    "Limit": self.page_size,
                },
            )
            if not isinstance(payload, dict) or not isinstance(payload.get("Items"), list):
                raise JellyfinResponseError("Jellyfin movie response was invalid")
            items = payload["Items"]
            for item in items:
                if isinstance(item, dict) and item.get("Type") == "BoxSet":
                    continue
                if not isinstance(item, dict) or not item.get("Id") or not item.get("Name") or not item.get("Path"):
                    raise JellyfinResponseError("Jellyfin movie response contained an invalid item")
                yield JellyfinMovie(
                    id=str(item["Id"]),
                    name=str(item["Name"]),
                    production_year=item.get("ProductionYear"),
                    server_path=str(item["Path"]),
                )
            start_index += len(items)
            total_record_count = payload.get("TotalRecordCount")
            if not items or (isinstance(total_record_count, int) and start_index >= total_record_count):
                return
