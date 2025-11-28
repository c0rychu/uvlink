import os
import subprocess
import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform == "win32" or os.name == "nt"


def is_link_or_junction(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def path_exists(path: Path) -> bool:
    return path.exists() or is_link_or_junction(path)


def create_windows_junction(symlink: Path, target: Path) -> None:
    """
    Windows junctions are similar to symlinks but specifically for directories.
    Does not require admin privileges as symlink_to.
    """
    if not target.is_dir():
        raise ValueError("Target must be an existing directory for Windows junction.")

    cmd = f'mklink /J "{symlink.as_posix()}" "{target.as_posix()}"'
    subprocess.check_call(cmd, shell=True)


def create_symlink(symlink: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    try:
        symlink.symlink_to(target, target_is_directory=target.is_dir())
    except OSError:
        if is_windows():
            create_windows_junction(symlink, target)
        else:
            raise
