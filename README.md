# uvlink
[![PyPI - Version](https://img.shields.io/pypi/v/uvlink)](https://pypi.org/project/uvlink/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/uvlink)](https://pypi.org/project/uvlink/)

`uvlink` is a CLI tool that moves `.venv` folders into a local cache and creates a symlink in your project, so cloud services like Dropbox or iCloud only sync your actual code—not hundreds of megabytes of dependencies.

- [Changelog](CHANGELOG.md)

> [!CAUTION]
> Since `v0.4.0`, the cache directory changed from `~/.local/share/uvlink/cache/venv/<project-name>-<hash>/venv` to `~/.local/share/uvlink/cache/<project-name>-<hash>/<venv_type>`. It is recommended to delete existing cached environments created with prior versions and rerun `uvlink link` to recreate them in the new structure.


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

Navigate to any Python project (which may be created by `uv init` for instance) and run:

```bash
$ cd /path/to/your/project
$ uvlink link
```

This creates a `.venv` symlink in your project pointing to a cached environment under `~/.local/share/uvlink/cache/<project-name>-<hash>/.venv`. Now your cloud service ignores the heavy virtual environment files.

After linking, you can do for example `uv sync` to install dependencies into `.venv`, which is now a symlink to the cached environment.

**List all linked projects:**

```bash
$ uvlink ls
```

Shows all projects having cached environments and whether their symlinks are still linked.

**Clean up unlinked caches:**

```bash
$ uvlink gc
```

Removes cached environments for projects that no longer have working symlinks, freeing up disk space.


## Demo
![](docs/fig/uvlink-demo@2x.gif)

## Advanced Usage

`uvlink` ships with a [Typer](https://typer.tiangolo.com/) CLI. Run `uvlink --help` for all options.

**Specify a project directory:**

```bash
$ uvlink --project-dir /path/to/project link
```

Works from any location without needing to `cd` into the project directory first.



## Notes
uvlink stores environments under `~/.local/share/uvlink/cache/<project-name>-<hash>/.venv` and makes a symlink `./.venv` back into that. Each project receives a stable hash based on its absolute path, so repeated runs target the same cache location.



## Contributing

Issues and pull requests are welcome. Please keep docstrings and comments in the Google style already used throughout the codebase and run the included linters/formatters before submitting. A pre-commit configuration is provided that runs Ruff and Black; install it with `pre-commit install` to match formatting.