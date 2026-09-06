# Jellyfin Renamer

A command-line tool for safely renaming local Jellyfin movie folders and files to match the title and production year stored in Jellyfin.

It only renames files and folders on disk. It does not change Jellyfin metadata or trigger a library refresh.

## Features

- Reads movie metadata from a Jellyfin server
- Matches an exact library name from Jellyfin
- Maps server-side paths to local paths using configurable prefixes
- Supports a dry-run mode before any filesystem changes are made
- Renames movie folders and files to a predictable pattern such as:

```text
Movies/
  In the Grey (2026)/
    In the Grey (2023).mp4
```

## Installation

### Prerequisites

- Python 3.11 or newer
- A Jellyfin server with an API key
- Access to the local media files you want to rename

### Install from source

Clone the repository and install it in a virtual environment:

```bash
git clone https://github.com/your-user/jellyfin-renamer.git
cd jellyfin-renamer
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

### Set the API key

The CLI reads the API key from the `JELLYFIN_API_KEY` environment variable:

```bash
export JELLYFIN_API_KEY="your-jellyfin-api-key"
```

On Windows PowerShell:

```powershell
$env:JELLYFIN_API_KEY = "your-jellyfin-api-key"
```

## Usage

After installation, the command is available as:

```bash
jellyfin-renamer --help
```

### Required arguments

```bash
jellyfin-renamer \
  --url "https://jellyfin.example.com" \
  --library "Movies" \
  --root "/data/Movies" \
  --server-prefix "/mnt/media" \
  --local-prefix "/data/Movies"
```

### Command arguments

- `--url`: Jellyfin server URL
- `--library`: Exact Jellyfin movie library name
- `--root`: Local library root directory
- `--server-prefix`: Jellyfin path prefix that matches the server-side media path
- `--local-prefix`: Local filesystem prefix that matches the same media on disk
- `--dry-run`: Show planned renames without making file system changes
- `--timeout`: HTTP timeout in seconds (default: `30.0`)
- `--insecure`: Skip TLS certificate verification for self-signed certificates

## Usage examples

### 1. Preview changes without renaming anything

```bash
export JELLYFIN_API_KEY="abc123"

jellyfin-renamer \
  --url "https://jellyfin.example.com" \
  --library "Movies" \
  --root "/home/user/Movies" \
  --server-prefix "/media" \
  --local-prefix "/home/user/Movies" \
  --dry-run
```

This prints each planned rename without modifying files.

### 2. Rename files on disk

```bash
export JELLYFIN_API_KEY="abc123"

jellyfin-renamer \
  --url "https://jellyfin.example.com" \
  --library "Movies" \
  --root "/home/user/Movies" \
  --server-prefix "/media" \
  --local-prefix "/home/user/Movies"
```

### 3. Use a self-signed local Jellyfin certificate

```bash
export JELLYFIN_API_KEY="abc123"

jellyfin-renamer \
  --url "https://jellyfin.local:8920" \
  --library "Movies" \
  --root "/srv/media" \
  --server-prefix "/mnt/media" \
  --local-prefix "/srv/media" \
  --insecure
```

## Typical folder mapping

If Jellyfin exposes a movie at `/mnt/media/Movies/In the Grey (2026)/In the Grey (2023).mp4` and your local copy is at `/home/user/Movies/In the Grey (2026)/In the Grey (2023).mp4`, then a mapping like this is appropriate:

```bash
--server-prefix "/mnt/media" \
--local-prefix "/home/user/Movies"
```

The tool figures out the matching local path and checks whether the filename or folder name should be changed to match the Jellyfin metadata.

## Notes

- Always run with `--dry-run` first to confirm the proposed renames.
- Verify that your `--library` name matches the exact Jellyfin library name.
- Make sure the root folder and local path prefixes point to the actual media library you want to rename.
