from pathlib import Path


def map_server_path(
    server_path: str | Path,
    server_prefix: str | Path,
    local_prefix: str | Path,
) -> Path:
    source = Path(server_path)
    prefix = Path(server_prefix)
    try:
        relative_path = source.relative_to(prefix)
    except ValueError as error:
        raise ValueError(f"Jellyfin path {source} is outside server prefix {prefix}") from error
    return Path(local_prefix) / relative_path


def ensure_within_root(path: Path, root: Path) -> Path:
    resolved_path = path.resolve(strict=False)
    resolved_root = root.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"Path {resolved_path} is outside configured root {resolved_root}") from error
    return resolved_path


def operation_paths(movie_path: Path, target_name: str) -> tuple[Path, Path]:
    if not movie_path.is_file():
        raise FileNotFoundError(f"Movie file does not exist: {movie_path}")
    source_directory = movie_path.parent
    destination_directory = source_directory.parent / target_name
    destination_file = destination_directory / f"{target_name}{movie_path.suffix}"
    return destination_directory, destination_file
