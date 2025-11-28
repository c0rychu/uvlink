"""Test for uvlink/cli.py"""

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
    expected_output = f"Would execute: ln -s {expected_venv} {expected_symlink}"
    assert result.stdout.strip() == expected_output

    # Verify that no symlink was actually created (dry-run should not create anything)
    assert not expected_symlink.exists()
    assert not expected_symlink.is_symlink()
    assert not expected_symlink.is_junction()


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
    assert expected_symlink.is_symlink() or expected_symlink.is_junction()

    # Verify the symlink actually points to the expected cache directory
    assert expected_symlink.resolve() == expected_venv.resolve()

    # Verify the cache directory exists
    assert expected_venv.exists()
    assert expected_venv.is_dir()


def test_ls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock XDG_DATA_HOME to use tmp_path for cache
    fake_home = tmp_path / "home"
    monkeypatch.setenv("XDG_DATA_HOME", str(fake_home))

    # Project 1: linked project - use `uvlink link` to create it properly
    project1_dir = tmp_path / "project1"
    project1_dir.mkdir()
    result1 = runner.invoke(app, ["--project-dir", str(project1_dir), "link"])
    assert result1.exit_code == 0
    p1 = Project(project_dir=project1_dir)

    # Project 2: unlinked project - use `uvlink link` then remove symlink
    # This simulates a realistic scenario where a project was linked but
    # the symlink was later removed (e.g., manually deleted or project moved)
    project2_dir = tmp_path / "project2"
    project2_dir.mkdir()
    result2 = runner.invoke(app, ["--project-dir", str(project2_dir), "link"])
    assert result2.exit_code == 0
    p2 = Project(project_dir=project2_dir)
    # Remove the symlink to make it unlinked
    symlink2 = project2_dir / ".venv"
    symlink2.unlink(missing_ok=True)

    # Use --cache-root to specify the cache directory explicitly
    cache_dir = fake_home / "uvlink" / "cache"
    result = runner.invoke(app, ["--cache-root", str(cache_dir), "ls"])
    assert result.exit_code == 0

    # Verify table structure
    assert "Cache-ID" in result.stdout
    assert "Project Path" in result.stdout
    assert "Is Linked" in result.stdout

    # Verify cache location message
    assert f"Cache Location: {cache_dir}" in result.stdout

    # Verify both projects appear and have correct linked status
    output_lines = result.stdout.split("\n")

    # Construct the cache IDs that appear in the table
    p1_cache_id = f"{p1.project_name}-{p1.project_hash}-{p1.venv_type}"
    p2_cache_id = f"{p2.project_name}-{p2.project_hash}-{p2.venv_type}"

    # Find lines containing each project
    p1_found = False
    p2_found = False

    for line in output_lines:
        # Check for project 1 (linked) - should have ✅
        if (
            p1.project_name in line
            or str(p1.project_dir) in line
            or p1_cache_id in line
        ):
            assert "✅" in line, f"Project 1 should be linked but found: {line}"
            p1_found = True

        # Check for project 2 (unlinked) - should have ❌
        if (
            p2.project_name in line
            or str(p2.project_dir) in line
            or p2_cache_id in line
        ):
            assert "❌" in line, f"Project 2 should be unlinked but found: {line}"
            p2_found = True

    assert p1_found, f"Project 1 ({p1.project_name}) not found in output"
    assert p2_found, f"Project 2 ({p2.project_name}) not found in output"
