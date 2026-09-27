"""uvlink command-line interface powered by Typer."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from uvlink import __version__
from uvlink.path_utils import create_symlink, path_exists
from uvlink.project import (
    DEFAULT_VENV_TYPE,
    Project,
    Projects,
    get_uvlink_dir,
    rm_rf,
)

app = typer.Typer(
    help=(
        f"uvlink {__version__} — keep .venv, node_modules, or any folder "
        "in a global cache and symlink it back."
    ),
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()

# Directory names offered by `uvlink link` when no VENV_TYPE is given.
# The first one is the default.
LINK_CHOICES = (DEFAULT_VENV_TYPE, "node_modules")


def is_interactive() -> bool:
    """Check whether we can show a menu.

    The menu reads keys from stdin and draws on stdout, so both must be a
    terminal. For example, `uvlink link > log.txt` is not interactive.

    Returns:
        bool: True if both stdin and stdout are terminals.
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def check_venv_type(name: str) -> bool | str:
    """Validate a VENV_TYPE typed into the menu.

    Args:
        name: Directory name typed by the user.

    Returns:
        bool | str: True if ``name`` is valid, else the error message.
            This is the format questionary's ``validate`` expects.
    """
    # sanitize_venv_type() turns "" into the default, but here the user
    # chose to type their own name, so an empty one is a mistake.
    if not name.strip():
        return "Name must not be empty"
    try:
        Project.sanitize_venv_type(name)
    except ValueError as e:
        return str(e)
    return True


TYPE_YOUR_OWN = "type your own"

MENU_COLOR = "#00e676"  # Vibrant green


def prompt_venv_type() -> str:
    """Ask which directory to link, from LINK_CHOICES or a custom name.

    Use the arrow keys to move and Enter to pick. The cursor starts on
    the first choice (``.venv``). Ctrl-C raises KeyboardInterrupt, which
    Typer turns into "Aborted!".

    Returns:
        str: The chosen directory name.
    """
    # Imported here since it takes ~100 ms and only this menu needs it.
    import questionary

    style = questionary.Style(
        [
            ("qmark", f"fg:{MENU_COLOR} bold"),
            ("pointer", f"fg:{MENU_COLOR} bold"),
            ("highlighted", f"fg:{MENU_COLOR} bold"),
            ("answer", f"fg:{MENU_COLOR} bold"),
        ]
    )
    choice: str = questionary.select(
        "Which directory to link?",
        choices=[*LINK_CHOICES, TYPE_YOUR_OWN],
        pointer="❯",  # noqa: RUF001 - intended, not a typo for ">"
        instruction="(↑/↓, Enter)",
        style=style,
    ).unsafe_ask()
    if choice == TYPE_YOUR_OWN:
        choice = questionary.text(
            "Directory name:", validate=check_venv_type, style=style
        ).unsafe_ask()
    return choice


def version_callback(value: bool) -> bool:
    """Print version when the eager flag is used."""

    if value:
        typer.echo(f"uvlink {__version__}")
        raise typer.Exit()
    return value


@app.callback()
def main(
    ctx: typer.Context,
    project_dir: Path | None = typer.Option(  # noqa: B008
        Path.cwd(),  # noqa: B008
        "--project-dir",
        "-p",
        show_default=True,
        dir_okay=True,
        file_okay=False,
        writable=True,
        resolve_path=True,
        help="Path to the project root; defaults to the current working directory.",
    ),
    cache_root: Path | None = typer.Option(  # noqa: B008
        None,
        "--cache-root",
        help=(
            "Override the cache root directory "
            "(defaults to XDG_DATA_HOME/uvlink/cache)."
        ),
    ),
    dry_run: bool | None = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        "-V",
        is_eager=True,
        callback=version_callback,
        help="Show uvlink version and exit.",
    ),
) -> None:
    ctx.obj = {
        "dry_run": dry_run,
        "cache_root": cache_root,
        "proj": Project(project_dir=project_dir, cache_root=cache_root),
    }


@app.command()
def link(
    ctx: typer.Context,
    venv_type: str | None = typer.Argument(
        None,
        metavar="[VENV_TYPE]",
        help=(
            "Directory name for the project symlink. If omitted, pick one from "
            "a menu (or use .venv when not run in a terminal)."
        ),
    ),
    dry_run: bool | None = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
) -> None:
    """Create (or update) the symlink in project pointing to the cached venv."""
    base_proj: Project = ctx.obj["proj"]
    cache_root = ctx.obj["cache_root"]
    dry_run = dry_run or ctx.obj["dry_run"]

    # Check before the menu, so the user doesn't answer it for nothing.
    if not dry_run and not base_proj.project_dir.is_dir():
        raise NotADirectoryError(f"{base_proj.project_dir} is not a directory")

    # Scripts and pipes can't answer a menu, so they keep the old default.
    if venv_type is None:
        venv_type = prompt_venv_type() if is_interactive() else DEFAULT_VENV_TYPE

    proj = Project(
        project_dir=base_proj.project_dir, venv_type=venv_type, cache_root=cache_root
    )

    symlink = proj.project_dir / f"{proj.venv_type}"
    venv = proj.project_cache_dir / f"{proj.venv_type}"
    if dry_run:
        typer.echo(f"Would execute: ln -s {venv} {symlink}")
        typer.Exit()

    else:
        if path_exists(venv):
            if typer.confirm(f"'{venv}' already exists, remove?", default=False):
                typer.echo("Removing...")
                rm_rf(venv.parent)
            else:
                typer.echo(f"Keep current {venv}")
        if path_exists(symlink):
            if typer.confirm(f"'{symlink}' already exists, overwrite?", default=False):
                rm_rf(symlink)
            else:
                typer.echo("Cancelled.")
                raise typer.Abort()

        create_symlink(symlink, venv)
        proj.save_json_metadata_file()
        typer.echo(f"symlink created: {symlink} -> {venv}")


@app.command("ls")
def list_venvs(
    ctx: typer.Context,
) -> None:
    """List status of existing projects."""
    cache_root = ctx.obj["cache_root"]
    ps = Projects(base_path=cache_root) if cache_root else Projects()
    linked = ps.get_list()
    table = Table(box=box.MINIMAL)

    table.add_column("Cache-ID", no_wrap=True)
    table.add_column("Project Path")
    table.add_column("Is Linked")

    for row in linked:
        table.add_row(
            row.project_name_hash,
            row.project_dir_str,
            "✅" if row.is_linked else "❌",
        )
    cache_location = cache_root if cache_root else get_uvlink_dir("cache")
    typer.secho(
        f"\n  Cache Location: {cache_location} / <Cache-ID>\n",
        fg="green",
    )
    console.print(table)


@app.command()
def gc(
    ctx: typer.Context,
    dry_run: bool | None = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
) -> None:
    """Remove cached venvs whose projects are no longer linked."""
    dry_run = dry_run or ctx.obj["dry_run"]
    cache_root = ctx.obj["cache_root"]
    ps = Projects(base_path=cache_root) if cache_root else Projects()
    link_infos = ps.get_list()
    for link_info in link_infos:
        if not link_info.is_linked:
            proj_cache = link_info.project.project_cache_dir
            if dry_run:
                typer.echo(f"Would remove {proj_cache.as_posix()}")
                continue
            else:
                if typer.confirm(f"Remove {proj_cache.as_posix()} ?", default=True):
                    typer.secho(f"Removing {proj_cache.as_posix()}", fg="red")
                    rm_rf(proj_cache)
                else:
                    typer.echo(f"Skiped {proj_cache.as_posix()}")


if __name__ == "__main__":  # pragma: no cover - convenience execution
    app()
