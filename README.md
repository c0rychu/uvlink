# uvlink

Keep project folders light by storing Python virtual environments in a single cache and linking them back into each repo. uvlink is handy when your projects live inside cloud-synced drives and you do not want `.venv` directories eating up bandwidth.


## Requirements

- Python 3.12+
- macOS or Linux shell with symlink support

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


## Usage

`uvlink` ships with a [Typer](https://typer.tiangolo.com/) CLI. Run `uvlink --help` (or `python -m uvlink.cli --help`) to view every option. 

Common commands:

```bash
$ uvlink link
```
This assumes your current working directory is a Python project folder.

Use
``` bash
$ uvlink --project-dir /path/to/project link
```
if you want to operate on a directory other than the current one.


## Notes

uvlink stores environments under `~/.local/share/uvlink/cache/<venv-type>/<project-name>-<hash>/venv` and makes a symlink `./.venv` back into that. Each project receives a stable hash based on its absolute path, so repeated runs target the same cache location.


## Contributing

Issues and pull requests are welcome. Please keep docstrings and comments in the Google style already used throughout the codebase and run the included linters/formatters before submitting. A pre-commit configuration is provided that runs Ruff and Black; install it with `pre-commit install` to match formatting.