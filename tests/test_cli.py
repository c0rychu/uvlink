"""Test for uvlink/cli.py"""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from uvlink.cli import app
from uvlink.project import Project

runner = CliRunner()


def test_version():
    from uvlink import __version__

    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == f"uvlink {__version__}"


def test_link_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock XDG_DATA_HOME to avoid touching real user data
    fake_home = tmp_path / "home"
    monkeypatch.setenv("XDG_DATA_HOME", str(fake_home))

    project_dir = tmp_path / "myproject"
    project_dir.mkdir()

    # Get expected paths for verification
    proj = Project(project_dir=project_dir)
    expected_symlink = project_dir / ".venv"
    expected_venv = proj.project_cache_dir / ".venv"

    result = runner.invoke(
        app, ["--project-dir", str(project_dir), "link", "--dry-run"]
    )
    assert result.exit_code == 0

    # Verify the output format matches what would be executed
    expected_output = f"ln -s {expected_venv} {expected_symlink}"
    assert result.stdout.strip() == expected_output

    # Verify that no symlink was actually created (dry-run should not create anything)
    assert not expected_symlink.exists()
    assert not expected_symlink.is_symlink()


def test_link_creation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock XDG_DATA_HOME to avoid touching real user data
    fake_home = tmp_path / "home"
    monkeypatch.setenv("XDG_DATA_HOME", str(fake_home))

    project_dir = tmp_path / "myproject"
    project_dir.mkdir()

    # Get expected paths for verification
    proj = Project(project_dir=project_dir)
    expected_symlink = project_dir / ".venv"
    expected_venv = proj.project_cache_dir / ".venv"

    result = runner.invoke(app, ["--project-dir", str(project_dir), "link"])
    assert result.exit_code == 0

    # Verify the output format matches the actual behavior
    expected_output = f"symlink created: {expected_symlink} -> {expected_venv}"
    assert expected_output in result.stdout

    # Verify symlink exists
    assert expected_symlink.is_symlink()

    # Verify the symlink actually points to the expected cache directory
    assert expected_symlink.resolve() == expected_venv.resolve()

    # Verify the cache directory exists
    assert expected_venv.exists()
    assert expected_venv.is_dir()

