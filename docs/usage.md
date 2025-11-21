# Usage

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

## Commands

### `link`

Creates the link and cache.

```bash
uvlink link [VENV_TYPE]
```

-   **`VENV_TYPE`**: Optional. Defaults to `.venv`. Useful if you need a different name like `.venv-prod`.

### `ls`

List all linked projects.

```bash
uvlink ls
```

Shows all projects having cached environments and whether their symlinks are still active.

### `gc`

Garbage collect unlinked caches.

```bash
uvlink gc
```

Removes cached environments for projects that no longer have working symlinks, freeing up disk space.

## Advanced Usage

### Specify Project Directory

You can run `uvlink` from anywhere by specifying the project directory:

```bash
uvlink --project-dir /path/to/project link
```

### Custom Venv Names

Swap the `.venv` folder name for something else:

```bash
uvlink link .my-custom-venv
```

## How it Works

`uvlink` stores environments under:

`~/.local/share/uvlink/cache/<project-name>-<hash>-<venv_type>/<venv_type>`

It then makes a symlink `./<venv_type>` back into that location. Each project receives a stable hash based on its absolute path, so repeated runs target the same cache location.
