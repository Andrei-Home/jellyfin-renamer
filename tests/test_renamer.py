from pathlib import Path

from jellyfin_renamer.renamer import execute_operation, plan_operation


def make_movie(tmp_path: Path, directory_name: str = "old") -> Path:
    directory = tmp_path / directory_name
    directory.mkdir()
    movie_file = directory / "old.mkv"
    movie_file.write_text("movie", encoding="utf-8")
    return movie_file


def test_dry_run_does_not_mutate_filesystem(tmp_path: Path) -> None:
    movie_file = make_movie(tmp_path)
    operation = plan_operation(movie_file, "Example Movie", 2023, tmp_path)

    result = execute_operation(operation, dry_run=True)

    assert result.status == "planned"
    assert movie_file.exists()
    assert not operation.destination_directory.exists()


def test_renames_file_and_directory(tmp_path: Path) -> None:
    movie_file = make_movie(tmp_path)
    operation = plan_operation(movie_file, "Example Movie", 2023, tmp_path)

    result = execute_operation(operation)

    renamed_file = tmp_path / "Example Movie (2023)" / "Example Movie (2023).mkv"
    assert result.status == "renamed"
    assert renamed_file.read_text(encoding="utf-8") == "movie"
    assert not movie_file.exists()


def test_skips_existing_destination(tmp_path: Path) -> None:
    movie_file = make_movie(tmp_path)
    destination = tmp_path / "Example Movie (2023)"
    destination.mkdir()
    operation = plan_operation(movie_file, "Example Movie", 2023, tmp_path)

    result = execute_operation(operation)

    assert result.status == "skipped"
    assert movie_file.exists()


def test_skips_already_canonical_movie(tmp_path: Path) -> None:
    movie_file = make_movie(tmp_path, "Example Movie (2023)")
    canonical_file = movie_file.parent / "Example Movie (2023).mkv"
    movie_file.rename(canonical_file)
    operation = plan_operation(canonical_file, "Example Movie", 2023, tmp_path)

    result = execute_operation(operation)

    assert result.status == "skipped"
