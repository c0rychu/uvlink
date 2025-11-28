---
icon: lucide/rocket
---

# uvlink

**uvlink** is a Python CLI tool that caches virtual environments outside your project and symlinks them back. Perfect for `uv` users who sync code to Dropbox, Google Drive, or iCloud. Only your source code syncs, not gigabytes of `.venv` dependencies.

[![PyPI - Version](https://img.shields.io/pypi/v/uvlink)](https://pypi.org/project/uvlink/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/uvlink)](https://pypi.org/project/uvlink/)
[![GitHub Actions - CI Tests](https://img.shields.io/github/actions/workflow/status/c0rychu/uvlink/ci-tests.yml?branch=main&label=CI%20Tests)](https://github.com/c0rychu/uvlink/actions/workflows/ci-tests.yml)
[![GitHub - License](https://img.shields.io/github/license/c0rychu/uvlink)](https://github.com/c0rychu/uvlink/blob/main/LICENSE)

## Why uvlink?

Cloud services like Dropbox, Google Drive, or iCloud often struggle with the thousands of small files found in Python virtual environments (`.venv`). This can lead to:

-   **Slow Syncing**: Endless "Syncing..." status.
-   **High Bandwidth Usage**: Uploading/downloading megabytes of dependencies unnecessarily.
-   **Conflicts**: Sync conflicts on binary files.

`uvlink` solves this by moving the heavy `.venv` directory to a local cache (outside the synced folder) and replacing it with a lightweight symlink. Your cloud service syncs the symlink (negligible size), while your tools (VS Code, terminal) follow the link seamlessly.

!!! warning "Important Note on Caching"
    Since `v0.6.0`, the cache directory includes the venv type in its folder name and stores the environment under a matching subdirectory (e.g. `~/.local/share/uvlink/cache/<project-name>-<hash>-.venv/.venv`). Delete caches created with older versions and rerun `uvlink link` to migrate.

!!! note "Windows Support"
    Windows support is considered beta as of `v0.8.0`. It uses directory junctions as a fallback when symlinks are not available, which does not require admin privileges or Developer Mode. Please report any issues you encounter on Windows!

## Quick Start

For installation instructions, please refer to the [Installation](installation.md) page.

Navigate to any Python project (which may be created by `uv init` for instance) and run `uvlink link`:

```bash
cd /path/to/your/project
uvlink link
```

The `link` command creates a `.venv` symlink in your project pointing to a cached environment. By default, it uses `.venv` as the symlink name because `uv sync` installs into `.venv` by default. You can use a different name if needed, for example:

```bash
uvlink link myenv
```

This creates a `myenv` symlink instead.

The cached environment is stored under `$XDG_DATA_HOME/uvlink/cache/<project-name>-<hash>-<venv_name>/<venv_name>` (or `~/.local/share/uvlink/cache/...` if `XDG_DATA_HOME` is not set).

After linking, you can use the virtual environment just like you would with `uv` within the project directory:

```bash
source .venv/bin/activate   # Activate the environment
uv sync                     # Install dependencies into the cached .venv
uv run python script.py     # Run commands in the environment
```

Since `.venv` exists as a symlink in your project directory, all standard activation methods work. Your cloud service will ignore the heavy virtual environment files since they're stored in the cache.

**List all cached environments:**

```bash
uvlink ls
```

Shows all projects with cached environments and their link status. Projects where the symlink has been removed (e.g., via `rm .venv`) will show as "Not Linked" (❌). You can relink them by running `uvlink link` again in that project directory.

**Remove a symlink**

To remove the symlink, just do normal `rm`:
```bash
rm .venv
```
This will remove the symlink `.venv`, and the unlinked cache can be further cleaned up by `uvlink gc` (garbage collection) command as following.

**Clean up unlinked caches:**

```bash
uvlink gc
```

Removes cached environments for projects that no longer have working symlinks (marked as "Not Linked" in `uvlink ls`), freeing up disk space.


## Demo
![](fig/uvlink-demo@2x.gif)


## Other Use Cases

In fact, since the minimal philosophy of uvlink is that it only creates symlinks and link them to the cache, it can be used for other use cases as well. For example, you can cache `tmp`, `objs`, ... etc as much as you want:
```bash
uvlink link .venv
uvlink link tmp
uvlink link objs
# ... etc
```
However, we only recommand using it for type of files that can be easily regenerated if lost, such as virtual environments, dependencies, intermediate build files, ... etc.