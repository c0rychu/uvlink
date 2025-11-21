---
icon: lucide/download
---

# Installation

## Requirements

-   **Python**: 3.12+
-   **OS**: macOS or Linux (with symlink support)

!!! warning "Platform Support"
    uvlink is currently only tested on Apple Silicon (M-series) machines running macOS Tahoe. Other operating systems or architectures have not been validated yet.

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
