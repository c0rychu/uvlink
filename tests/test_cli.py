"""Test for uvlink/cli.py"""

from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

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


@pytest.mark.parametrize("args", [["-h"], ["link", "-h"], ["ls", "-h"], ["gc", "-h"]])
def test_short_help(args: list[str]) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


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


class FakeQuestion:
    """Stands in for a questionary prompt.

    .unsafe_ask() returns ``answer``, or raises it if it's an exception
    (e.g. KeyboardInterrupt for Ctrl-C).
    """

    def __init__(self, answer: str | BaseException) -> None:
        self.answer = answer

    def unsafe_ask(self) -> str:
        if isinstance(self.answer, BaseException):
            raise self.answer
        return self.answer


def not_called(*args: object, **kwargs: object) -> NoReturn:
    raise AssertionError("the menu should not be shown")


@pytest.fixture
def menu(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[..., Path]:
    """Pretend to be in a terminal and script the menu answers.

    Returns a function that takes the answers for the select and text
    prompts, and returns a fresh project dir.
    """
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "home"))
    # CliRunner's stdin is not a TTY, so pretend it is to get the menu.
    monkeypatch.setattr("uvlink.cli.is_interactive", lambda: True)

    def setup(selected: str | BaseException, typed: str | BaseException = "") -> Path:
        monkeypatch.setattr(
            "questionary.select", lambda *a, **kw: FakeQuestion(selected)
        )
        monkeypatch.setattr("questionary.text", lambda *a, **kw: FakeQuestion(typed))
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        return project_dir

    return setup


@pytest.mark.parametrize(
    ("selected", "typed", "expected_name"),
    [
        (".venv", "", ".venv"),
        ("node_modules", "", "node_modules"),
        ("type your own", "my-env", "my-env"),
    ],
)
def test_link_menu(
    menu: Callable[..., Path], selected: str, typed: str, expected_name: str
) -> None:
    project_dir = menu(selected, typed)

    result = runner.invoke(app, ["--project-dir", str(project_dir), "link"])
    assert result.exit_code == 0, result.stdout

    symlink = project_dir / expected_name
    assert symlink.is_symlink() or symlink.is_junction()


@pytest.mark.parametrize(
    ("selected", "typed"),
    [
        (KeyboardInterrupt(), ""),  # Ctrl-C at the menu
        ("type your own", KeyboardInterrupt()),  # Ctrl-C at the name prompt
    ],
)
def test_link_menu_ctrl_c(
    menu: Callable[..., Path],
    selected: str | BaseException,
    typed: str | BaseException,
) -> None:
    project_dir = menu(selected, typed)

    result = runner.invoke(app, ["--project-dir", str(project_dir), "link"])
    assert result.exit_code == 130  # Typer's exit code for Ctrl-C (128 + SIGINT)
    assert list(project_dir.iterdir()) == []


def test_link_menu_dry_run(menu: Callable[..., Path]) -> None:
    project_dir = menu("node_modules")

    result = runner.invoke(
        app, ["--project-dir", str(project_dir), "link", "--dry-run"]
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("Would execute: ln -s ")
    assert result.stdout.strip().endswith(str(project_dir / "node_modules"))
    assert list(project_dir.iterdir()) == []


def test_link_menu_not_shown_for_missing_project_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("uvlink.cli.is_interactive", lambda: True)
    monkeypatch.setattr("questionary.select", not_called)

    result = runner.invoke(app, ["--project-dir", str(tmp_path / "missing"), "link"])
    assert isinstance(result.exception, NotADirectoryError)


def test_link_without_terminal_uses_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "home"))
    monkeypatch.setattr("uvlink.cli.is_interactive", lambda: False)
    monkeypatch.setattr("questionary.select", not_called)
    project_dir = tmp_path / "myproject"
    project_dir.mkdir()

    result = runner.invoke(app, ["--project-dir", str(project_dir), "link"])
    assert result.exit_code == 0
    assert (project_dir / ".venv").is_symlink() or (project_dir / ".venv").is_junction()


@pytest.mark.parametrize(
    ("stdin_tty", "stdout_tty", "expected"),
    [(True, True, True), (True, False, False), (False, True, False)],
)
def test_is_interactive(
    monkeypatch: pytest.MonkeyPatch, stdin_tty: bool, stdout_tty: bool, expected: bool
) -> None:
    from uvlink.cli import is_interactive

    monkeypatch.setattr("sys.stdin.isatty", lambda: stdin_tty)
    monkeypatch.setattr("sys.stdout.isatty", lambda: stdout_tty)
    assert is_interactive() is expected


def test_check_venv_type() -> None:
    from uvlink.cli import check_venv_type

    assert check_venv_type("my-env") is True
    assert "path separators" in str(check_venv_type("a/b"))
    assert "empty" in str(check_venv_type(""))
    assert "empty" in str(check_venv_type("   "))
