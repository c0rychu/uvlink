# uvlink
[![PyPI - Version](https://img.shields.io/pypi/v/uvlink)](https://pypi.org/project/uvlink/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/uvlink)](https://pypi.org/project/uvlink/)

`uvlink` is a Python CLI tool that caches virtual environments outside your project and symlinks them back. Perfect for `uv` users who sync code to Dropbox, Google Drive, or iCloud. Only your source code syncs, not gigabytes of `.venv` dependencies.

- [Documentation](https://c0rychu.github.io/uvlink/)
- [Changelog](docs/CHANGELOG.md)

> [!CAUTION]
> Since `v0.6.0`, the cache directory includes the venv type in its folder name and stores the environment under a matching subdirectory (e.g. `~/.local/share/uvlink/cache/<project-name>-<hash>-.venv/.venv`). Delete caches created with older versions and rerun `uvlink link` to migrate.


## Requirements

- Python 3.12+
- macOS or Linux with symlink support

> [!WARNING]
> uvlink is currently only tested on Apple Silicon (M-series) machines running macOS Tahoe. Other operating systems or architectures have not been validated yet.



## Install

### Using `uv tool` (recommended)

```bash
$ uv tool install uvlink
```

This installs the CLI into your `~/.local/bin` (or platform equivalent) with isolated dependencies handled by [Astral's uv](https://docs.astral.sh/uv/).

### Using `pip`

```bash
$ pip install uvlink
```


## Quick Start

Navigate to any Python project (which may be created by `uv init` for instance) and run `uvlink link`:

```bash
$ cd /path/to/your/project
$ uvlink link
```

The `link` command creates a `.venv` symlink in your project pointing to a cached environment. By default, it uses `.venv` as the symlink name because `uv sync` installs into `.venv` by default. You can use a different name if needed, for example:

```bash
$ uvlink link myenv
```

This creates a `myenv` symlink instead. 

The cached environment is stored under `$XDG_DATA_HOME/uvlink/cache/<project-name>-<hash>-<venv_name>/<venv_name>` (or `~/.local/share/uvlink/cache/...` if `XDG_DATA_HOME` is not set).

After linking, you can use the virtual environment just like you would with `uv` whithin the project directory:

```bash
$ source .venv/bin/activate  # Activate the environment
$ uv sync                    # Install dependencies into the cached .venv
$ uv run python script.py    # Run commands in the environment
```

Since `.venv` exists as a symlink in your project directory, all standard activation methods work. Your cloud service will ignore the heavy virtual environment files since they're stored in the cache.

**List all cached environments:**

```bash
$ uvlink ls
```

Shows all projects with cached environments and their link status. Projects where the symlink has been removed (e.g., via `rm .venv`) will show as "Not Linked" (❌). You can relink them by running `uvlink link` again in that project directory.

**Clean up unlinked caches:**

```bash
$ uvlink gc
```

Removes cached environments for projects that no longer have working symlinks (marked as "Not Linked" in `uvlink ls`), freeing up disk space.


## Demo
![](docs/fig/uvlink-demo@2x.gif)

## Advanced Usage

`uvlink` ships with a [Typer](https://typer.tiangolo.com/) CLI. Run `uvlink --help` for all available options and commands.

**Specify a project directory:**

```bash
$ uvlink --project-dir /path/to/project link
```

Works from any location without needing to `cd` into the project directory first.

**Swap the .venv folder name:**

```bash
$ uvlink --project-dir /path/to/project link [VENV_TYPE]
```

Custom `[VENV_TYPE]` are helpful when sharing a cache across tooling expectations (e.g., `.venv-prod`, `.venv-dev`).

**Custom Cache Location:**

The default cache location is `$XDG_DATA_HOME/uvlink/cache` if `XDG_DATA_HOME` is set, otherwise it falls back to `~/.local/share/uvlink/cache`.

To override the cache location, you can either:

1. Set the `XDG_DATA_HOME` environment variable:
   ```bash
   $ export XDG_DATA_HOME=/my/custom/path
   $ uvlink link
   ```

2. Use the `--cache-root` option (must be used consistently across all commands):
   ```bash
   $ uvlink --cache-root /path/to/cache link
   $ uvlink --cache-root /path/to/cache ls
   $ uvlink --cache-root /path/to/cache gc
   ```

   Note: When using `--cache-root`, you must specify it for every command (`link`, `ls`, `gc`). Consider setting up a shell alias to avoid repetition:
   ```bash
   $ alias uvlink='uvlink --cache-root /my/cache/root'
   ```



## How It Works

`uvlink` stores environments under `$XDG_DATA_HOME/uvlink/cache/<project-name>-<hash>-<venv_name>/<venv_name>` (or `~/.local/share/uvlink/cache/...` if `XDG_DATA_HOME` is not set) and creates a symlink `<venv_name>` in your project directory pointing to that cached location.

Each project receives a stable hash based on its absolute path, so repeated runs target the same cache location. The symlink behaves like a regular `.venv` directory for most purposes. You can activate it with `source .venv/bin/activate` or use `uv run` commands as usual.

**What `uvlink` does:**
- Creates a symlink `.venv` (or your custom name) in your project directory
- Stores the actual virtual environment in a centralized cache location

**What `uvlink` does NOT do:**
- It does not install packages (use `uv sync`, `uv add`, `uv pip install`, etc.)
- It does not remove symlinks (use `rm .venv` if you want to unlink and run `uvlink gc` after unlink to clean up the unlinked caches.)
- It does not manage or activate environments (use standard `uv` commands)



## Contributing

Issues and pull requests are welcome. Please keep docstrings and comments in the Google style already used throughout the codebase and run the included linters/formatters before submitting. A pre-commit configuration is provided that runs Ruff and Black; install it with `pre-commit install` to match formatting.