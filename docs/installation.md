---
icon: lucide/download
---

# Installation

## Requirements

-   **Python**: 3.12+
-   **OS**: macOS, Linux, and Windows(beta support)

!!! note "Windows Support"
    Windows support is considered beta as of `v0.8.0`. It uses directory junctions as a fallback when symlinks are not available, which does not require admin privileges or Developer Mode. Please report any issues you encounter on Windows!

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
