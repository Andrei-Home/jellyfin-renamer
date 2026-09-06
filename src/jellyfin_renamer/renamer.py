from pathlib import Path

from .models import OperationResult, RenameOperation
from .naming import format_movie_name
from .paths import ensure_within_root, operation_paths


def plan_operation(
    movie_path: Path,
    movie_name: str,
    production_year: int | None,
    root: Path,
) -> RenameOperation:
    source_file = ensure_within_root(movie_path, root)
    target_name = format_movie_name(movie_name, production_year)
    source_directory = ensure_within_root(source_file.parent, root)
    destination_directory, destination_file = operation_paths(source_file, target_name)
    ensure_within_root(destination_directory, root)
    return RenameOperation(
        source_file=source_file,
        destination_file=destination_file,
        source_directory=source_directory,
        destination_directory=destination_directory,
    )


def execute_operation(operation: RenameOperation, dry_run: bool = False) -> OperationResult:
    if not operation.source_file.is_file():
        return OperationResult(operation, "failed", "Source movie file does not exist")

    directory_changes = operation.source_directory != operation.destination_directory
    file_changes = operation.source_file != operation.destination_file

    if not directory_changes and not file_changes:
        return OperationResult(operation, "skipped", "Already has the canonical name")

    if directory_changes and operation.destination_directory.exists():
        return OperationResult(operation, "skipped", "Destination movie directory already exists")
    if file_changes and operation.destination_file.exists():
        return OperationResult(operation, "skipped", "Destination movie file already exists")

    if dry_run:
        return OperationResult(operation, "planned", "Ready to rename")

    try:
        if directory_changes:
            operation.source_directory.rename(operation.destination_directory)
            if file_changes:
                moved_source_file = operation.destination_directory / operation.source_file.name
                moved_source_file.rename(operation.destination_file)
        elif file_changes:
            operation.source_file.rename(operation.destination_file)
    except OSError as error:
        return OperationResult(operation, "failed", str(error))

    return OperationResult(operation, "renamed", "Renamed successfully")
