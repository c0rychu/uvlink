---
icon: lucide/download
---

# Installation

## Requirements

-   **Python**: 3.12+
-   **OS**: macOS or Linux (with symlink support)

!!! warning "Platform Support"
    Windows is not supported yet, but contributions/discussions/testing are welcome! See [related issues with `os:Windows` label](https://github.com/c0rychu/uvlink/issues?q=is%3Aissue%20state%3Aopen%20label%3Aos%3AWindows) for more details.

## Install Methods

### Using `uv tool` (Recommended)

The best way to install `uvlink` is using [Astral's uv](https://docs.astral.sh/uv/), which manages it as an isolated tool.

```bash
uv tool install uvlink
```

This installs the CLI into your `~/.local/bin` (or platform equivalent).

### Using `pip`

You can also install it via standard pip:

```bash
pip install uvlink
```
