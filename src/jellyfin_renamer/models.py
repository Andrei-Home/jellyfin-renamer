from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class JellyfinLibrary:
    id: str
    name: str
    collection_type: str | None


@dataclass(frozen=True)
class JellyfinMovie:
    id: str
    name: str
    production_year: int | None
    server_path: str
    item_type: str | None = None


@dataclass(frozen=True)
class RenameOperation:
    source_file: Path
    destination_file: Path
    source_directory: Path
    destination_directory: Path


@dataclass(frozen=True)
class OperationResult:
    operation: RenameOperation
    status: Literal["planned", "renamed", "skipped", "failed"]
    message: str
