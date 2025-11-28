"""Test for uvlink/project.py"""

from pathlib import Path

import pytest

from uvlink.path_utils import create_symlink, is_windows
from uvlink.project import Project


class TestProject:
    def test_hash_path(self):
        expected_hash = "d0023e7cb6a9" if is_windows() else "8a5edab28263"
        assert Project.hash_path("/") == expected_hash

    def test_project_init_path_resolution_with_tilde(self) -> None:
        """Test with tilde expansion and parent directory (e.g., "~/../xxx")."""
        user_home_path = Path.home()
        test_dir = user_home_path / "test_project"

        # Test ~/test_project resolves correctly
        p2 = Project(project_dir="~/test_project")
        assert p2.project_dir == test_dir.resolve()
        assert p2.project_dir.is_absolute()

        # Test ~/.. resolves to parent of HOME
        p3 = Project(project_dir="~/..")
        assert p3.project_dir == user_home_path.parent.resolve()
        assert p3.project_dir.is_absolute()

    def test_project_init(self, tmp_path: Path) -> None:
        p = Project(project_dir=tmp_path)
        # Project.resolve() normalizes the path, so compare with resolved tmp_path
        assert p.project_dir == tmp_path.resolve()
        assert p.project_name == tmp_path.name
        assert p.venv_type == ".venv"
        assert "uvlink/cache" in p.project_cache_dir.as_posix()

    def test_project_init_path_resolution(self, tmp_path: Path) -> None:
        """Test that Project resolves relative paths and parent directory references."""
        # Create a subdirectory to test relative paths with parent directory references
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Test with relative path containing parent directory
        # (e.g., "subdir/nested/../..")
        relative_path = str(subdir / ".." / "..")
        p1 = Project(project_dir=relative_path)
        # Should resolve to the absolute tmp_path
        assert p1.project_dir == tmp_path.resolve()
        assert p1.project_dir.is_absolute()
        assert p1.project_name == tmp_path.name

        # Test symlink resolution
        # Create a target directory and a symlink pointing to it
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        symlink_path = tmp_path / "symlink"
        create_symlink(symlink_path, target_dir)

        # Project should resolve the symlink to the actual target
        p4 = Project(project_dir=symlink_path)
        assert p4.project_dir == target_dir.resolve()
        assert p4.project_dir.is_absolute()
        # The project name should be the target directory's name (after resolution)
        assert p4.project_name == target_dir.name

    def test_metadata_roundtrip(self, tmp_path: Path) -> None:
        # Test with default venv_type
        p1 = Project(project_dir=tmp_path)
        # Mock the cache dir to be inside tmp_path so we can write to it
        p1.project_cache_dir = tmp_path / "cache" / "hash1"

        json_path1 = p1.save_json_metadata_file()
        assert json_path1.exists()

        p1_loaded = Project.from_json(json_path1)
        assert p1_loaded.project_dir == p1.project_dir
        assert p1_loaded.venv_type == p1.venv_type
        assert p1_loaded.venv_type == ".venv"

        # Test with custom venv_type
        p2 = Project(project_dir=tmp_path, venv_type="myvenv")
        # Mock the cache dir to be inside tmp_path so we can write to it
        p2.project_cache_dir = tmp_path / "cache" / "hash2"

        json_path2 = p2.save_json_metadata_file()
        assert json_path2.exists()

        p2_loaded = Project.from_json(json_path2)
        assert p2_loaded.project_dir == p2.project_dir
        assert p2_loaded.venv_type == p2.venv_type
        assert p2_loaded.venv_type == "myvenv"

    def test_sanitize_venv_type(self):
        assert Project.sanitize_venv_type(None) == ".venv"
        assert Project.sanitize_venv_type("myvenv") == "myvenv"

        with pytest.raises(ValueError, match="must not be empty"):
            Project.sanitize_venv_type("   ")
        with pytest.raises(ValueError, match="path separators"):
            Project.sanitize_venv_type("a/b")
        with pytest.raises(ValueError, match="only contain letters"):
            Project.sanitize_venv_type("a$b")


def test_get_uvlink_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Use tmp_path instead of hardcoded /tmp path for better cleanup
    fake_xdg = tmp_path / "fake_xdg"
    monkeypatch.setenv("XDG_DATA_HOME", str(fake_xdg))
    from uvlink.project import get_uvlink_dir

    assert get_uvlink_dir() == fake_xdg / "uvlink"
    assert get_uvlink_dir("cache") == fake_xdg / "uvlink" / "cache"
