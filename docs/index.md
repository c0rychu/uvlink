---
icon: lucide/rocket
---

# uvlink

**uvlink** is a CLI tool that moves `.venv` folders into a local cache and creates a symlink in your project.

[![PyPI - Version](https://img.shields.io/pypi/v/uvlink)](https://pypi.org/project/uvlink/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/uvlink)](https://pypi.org/project/uvlink/)

## Why uvlink?

Cloud services like Dropbox, iCloud, or Google Drive often struggle with the thousands of small files found in Python virtual environments (`.venv`). This can lead to:

-   **Slow Syncing**: Endless "Syncing..." status.
-   **High Bandwidth Usage**: Uploading/downloading megabytes of dependencies unnecessarily.
-   **Conflicts**: Sync conflicts on binary files.

`uvlink` solves this by moving the heavy `.venv` directory to a local cache (outside the synced folder) and replacing it with a lightweight symlink. Your cloud service syncs the symlink (negligible size), while your tools (VS Code, terminal) follow the link seamlessly.

!!! warning "Important Note on Caching"
    Since `v0.6.0`, the cache directory includes the venv type in its folder name and stores the environment under a matching subdirectory. If you have caches from older versions, delete them and rerun `uvlink link` to migrate.

## Quick Start

Navigate to any Python project and run:

```bash
cd /path/to/your/project
uvlink link
```

This creates a `.venv` symlink in your project pointing to a cached environment under `~/.local/share/uvlink/cache/...`.

After linking, you can use standard commands:

```bash
uv sync
```

This installs dependencies into the cached environment via the symlink.


## Demo
![](fig/uvlink-demo@2x.gif)