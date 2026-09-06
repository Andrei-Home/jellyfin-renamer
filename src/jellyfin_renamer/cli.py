import argparse
import os
from pathlib import Path

from .client import JellyfinClient, JellyfinError
from .paths import map_server_path
from .renamer import execute_operation, plan_operation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely rename Jellyfin movie files and folders")
    parser.add_argument("--url", required=True, help="Jellyfin server URL")
    parser.add_argument("--library", required=True, help="Exact Jellyfin movie library name")
    parser.add_argument("--root", required=True, type=Path, help="Local library root")
    parser.add_argument("--server-prefix", required=True, help="Jellyfin path prefix")
    parser.add_argument("--local-prefix", required=True, help="Local path prefix")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without modifying files")
    parser.add_argument(
        "--refresh-library",
        action="store_true",
        help="Refresh the Jellyfin library after successful renames",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    api_key = os.environ.get("JELLYFIN_API_KEY")
    if not api_key:
        parser.error("JELLYFIN_API_KEY is required")

    client = JellyfinClient(args.url, api_key, args.timeout, not args.insecure)
    try:
        library = client.select_movie_library(args.library)
        had_failure = False
        for movie in client.movies(library.id):
            local_path = map_server_path(movie.server_path, args.server_prefix, args.local_prefix)
            operation = plan_operation(local_path, movie.name, movie.production_year, args.root)
            result = execute_operation(operation, dry_run=args.dry_run)
            had_failure = had_failure or result.status == "failed"
            print(
                f"{result.status}: {result.operation.source_file} -> "
                f"{result.operation.destination_file} ({result.message})"
            )
        if args.refresh_library and not args.dry_run and not had_failure:
            client.refresh_library()
            print(f"refreshed: {library.name}")
    except (JellyfinError, OSError, ValueError) as error:
        print(f"error: {error}")
        return 1
    return 1 if had_failure else 0
