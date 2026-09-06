# Jellyfin Renamer

A command-line tool for safely aligning local Jellyfin movie folders and files with their Jellyfin title and production year.

The initial implementation is under development. It will use an API key from `JELLYFIN_API_KEY`, support exact library-name selection, configurable server-to-local path mappings, and a read-only dry run before any filesystem changes.

Expected layout:

```text
Movies/
  In the Grey (2026)/
    In the Grey (2023).mp4
```

The tool will rename local files and folders only. It will not modify Jellyfin metadata or trigger a library refresh automatically.
