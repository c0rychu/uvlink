---
icon: lucide/terminal
---

# Usage

## Commands

### `link`

Creates the symlink and cache. The `link` command creates a `.venv` symlink in your project pointing to a cached environment. By default, it uses `.venv` as the symlink name because `uv sync` installs into `.venv` by default.

```bash
uvlink link [VENV_TYPE]
```

-   **`VENV_TYPE`**: Optional. Defaults to `.venv`. You can use a different name if needed, for example `uvlink link myenv` creates a `myenv` symlink instead.

### `ls`

List all cached environments.

```bash
uvlink ls
```

Shows all projects with cached environments and their link status. Projects where the symlink has been removed (e.g., via `rm .venv`) will show as "Not Linked" (❌). You can relink them by running `uvlink link` again in that project directory.

### `gc`

Garbage collect unlinked caches.

```bash
uvlink gc
```

Removes cached environments for projects that no longer have working symlinks (marked as "Not Linked" in `uvlink ls`), freeing up disk space.


### Activating Virtual Environments

After linking, you can use the virtual environment just like you would with `uv`:

```bash
source .venv/bin/activate   # Activate the environment
uv sync                     # Install dependencies into the cached .venv
uv run python script.py     # Run commands in the environment
```

Since `.venv` exists as a symlink in your project directory, all standard activation methods work.


## Advanced Usage

### Specify Project Directory

You can run `uvlink` from anywhere by specifying the project directory:

```bash
uvlink --project-dir /path/to/project link
```

### Custom Venv Names

Swap the `.venv` symlink name for something else:

```bash
uvlink link .my-custom-venv
```

### Custom Cache Location

The default cache location is `$XDG_DATA_HOME/uvlink/cache` if `XDG_DATA_HOME` is set, otherwise it falls back to `~/.local/share/uvlink/cache`.

To override the cache location, you can either:

1. Set the `XDG_DATA_HOME` environment variable:
   ```bash
   export XDG_DATA_HOME=/my/custom/path
   uvlink link
   ```
>!!! warning "Important"
     This will affect other software using `XDG_DATA_HOME` environment variable as well!

2. Use the `--cache-root` option (must be used consistently across all commands):
   ```bashå
   uvlink --cache-root /path/to/cache link
   uvlink --cache-root /path/to/cache ls
   uvlink --cache-root /path/to/cache gc
   ```

   Note: When using `--cache-root`, you must specify it for every command (`link`, `ls`, `gc`). Consider setting up a shell alias to avoid repetition:
   ```bash
   alias uvlink='uvlink --cache-root /my/cache/root'
   ```

## How it Works

`uvlink` stores environments under `$XDG_DATA_HOME/uvlink/cache/<project-name>-<hash>-<venv_name>/<venv_name>` (or `~/.local/share/uvlink/cache/...` if `XDG_DATA_HOME` is not set) and creates a symlink `<venv_name>` in your project directory pointing to that cached location.

Each project receives a stable hash based on its absolute path, so repeated runs target the same cache location. The symlink behaves like a regular `.venv` directory for most purposes. You can activate it with `source .venv/bin/activate` or use `uv run` commands as usual.

**What `uvlink` does:**

- Creates a symlink `.venv` (or your custom name) in your project directory
- Stores the actual virtual environment in a centralized cache location

**What `uvlink` does NOT do:**

- It does not install packages (use `uv sync`, `uv add`, `uv pip install`, etc.)
- It does not remove symlinks (use `rm .venv` if you want to unlink and run `uvlink gc` after unlink to clean up the unlinked caches)
- It does not manage or activate environments (use standard `uv` commands)
