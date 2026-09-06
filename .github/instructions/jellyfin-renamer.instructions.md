---
name: Jellyfin Renamer Python
description: "Use when changing the Jellyfin Renamer Python package or its pytest tests. Covers Jellyfin API safety, filesystem rename rules, path validation, and project testing conventions."
applyTo: "src/**/*.py, tests/**/*.py"
---

# Jellyfin Renamer Guidelines

## Project Structure

- Target Python 3.11 or newer.
- Preserve the `src/jellyfin_renamer/` package layout and use relative imports.
- Keep API access, models, naming, path validation, planning, mutation, and CLI orchestration in their existing modules.
- Use type annotations throughout and frozen dataclasses for structured data.
- Prefer `pathlib.Path` for filesystem operations.

## Jellyfin API

- Read the API key only from `JELLYFIN_API_KEY`; never hard-code, print, or include it in error messages.
- Keep TLS certificate verification enabled by default. Any insecure mode must be explicit and opt-in.
- Use request timeouts and descriptive domain-specific errors.
- Preserve exact library-name matching, duplicate detection, movie-library validation, response validation, and pagination.
- Use fake HTTP opener/response objects in tests; do not require a live Jellyfin server.

## Filesystem Safety

- Map Jellyfin server paths to local paths through the configured prefixes.
- Resolve paths and reject anything outside the configured local library root, including symlink escapes.
- Never overwrite an existing destination file or directory; skip and report collisions.
- Preserve the movie file extension and rename only the exact file represented by the Jellyfin item.
- Leave subtitles, artwork, extras, trailers, samples, editions, and unrelated files untouched unless explicitly requested.
- Keep `--dry-run` completely non-mutating while still performing API reads and filesystem inspection.
- Do not modify Jellyfin metadata or trigger a library refresh automatically.
- Treat directory/file rename failures as partial-operation risks and report them clearly.

## Tests

- Add focused pytest coverage for every behavior change.
- Use `tmp_path` for filesystem scenarios and verify both filesystem state and operation results.
- Cover missing years, invalid names, path escapes, collisions, dry-run immutability, API failures, pagination, and partial failures when relevant.
- Run the narrowest affected test file first, then run `python -m pytest` before finishing.
