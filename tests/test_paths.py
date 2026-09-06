from pathlib import Path

import pytest

from jellyfin_renamer.paths import ensure_within_root, map_server_path, operation_paths


def test_maps_server_path_to_local_path() -> None:
    result = map_server_path("/media/movies/example/movie.mkv", "/media/movies", "/mnt/movies")
    assert result == Path("/mnt/movies/example/movie.mkv")


def test_rejects_path_outside_server_prefix() -> None:
    with pytest.raises(ValueError):
        map_server_path("/media/tv/show.mkv", "/media/movies", "/mnt/movies")


def test_ensure_within_root_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "movies"
    root.mkdir()
    with pytest.raises(ValueError):
        ensure_within_root(root / ".." / "outside.mkv", root)


def test_builds_folder_and_file_destinations(tmp_path: Path) -> None:
    source_directory = tmp_path / "old"
    source_directory.mkdir()
    movie_path = source_directory / "old.mkv"
    movie_path.touch()

    destination_directory, destination_file = operation_paths(movie_path, "New Name (2023)")

    assert destination_directory == tmp_path / "New Name (2023)"
    assert destination_file == destination_directory / "New Name (2023).mkv"
