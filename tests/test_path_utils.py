from pathlib import Path

import pytest

from uvlink.path_utils import create_symlink, create_windows_junction, is_windows


def test_create_symlink(tmp_path: Path):
    target_dir = tmp_path / "target"
    symlink_dir = tmp_path / "symlink"
    create_symlink(symlink=symlink_dir, target=target_dir)

    assert symlink_dir.exists()
    assert symlink_dir.is_symlink() or (is_windows() and symlink_dir.is_junction())
    assert symlink_dir.resolve() == target_dir.resolve()


@pytest.mark.skipif(
    not is_windows(), reason="Windows junctions are only applicable on Windows."
)
def test_create_windows_junction(tmp_path: Path):
    target_dir = tmp_path
    symlink_dir = tmp_path / "symlink"
    create_windows_junction(symlink=symlink_dir, target=target_dir)

    assert symlink_dir.exists()
    assert symlink_dir.is_junction()
    assert symlink_dir.resolve() == target_dir.resolve()


def test_create_windows_junction_invalid_target(tmp_path: Path):
    with pytest.raises(ValueError):
        create_windows_junction(
            symlink=tmp_path / "any", target=tmp_path / "nonexistent"
        )
