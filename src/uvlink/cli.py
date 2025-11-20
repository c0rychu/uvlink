"""uvlink command-line interface powered by Typer."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from uvlink import __version__
from uvlink.project import Project, Projects, get_uvlink_dir, rm_rf

app = typer.Typer(
    help=f"uvlink {__version__} — create .venv in global cache and symlink back.",
    no_args_is_help=True,
)

console = Console()


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
    dry_run: bool | None = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
    _version: bool = typer.Option(  # noqa: B008
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
        "proj": Project(project_dir=project_dir),
    }


@app.command()
def link(
    ctx: typer.Context,
    venv_type: str = typer.Argument(
        ".venv",
        metavar="[VENV_TYPE]",
        help="Optional directory name for the project symlink (defaults to .venv).",
    ),
    dry_run: bool | None = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
) -> None:
    """Create (or update) the symlink in project pointing to the cached venv."""
    # Get project_dir from ctx and update venv_type from CLI argument
    base_proj: Project = ctx.obj["proj"]
    proj = Project(project_dir=base_proj.project_dir, venv_type=venv_type)

    # Set dry_run flag
    dry_run = dry_run or ctx.obj["dry_run"]

    symlink = proj.project_dir / f"{proj.venv_type}"
    venv = proj.project_cache_dir / f"{proj.venv_type}"
    if dry_run:
        typer.echo(f"ln -s {venv} {symlink}")
        typer.Exit()

    else:
        if not proj.project_dir.is_dir():
            raise NotADirectoryError(f"{proj.project_dir} is not a directory")
        else:
            if venv.exists() or venv.is_symlink():
                if typer.confirm(f"'{venv}' already exist, remove?", default=True):
                    typer.echo("Removing...")
                    rm_rf(venv.parent)
                else:
                    typer.echo(f"Keep current {venv}")
            if symlink.exists() or symlink.is_symlink():
                if typer.confirm(
                    f"'{symlink}' already exist, overwrite?", default=True
                ):
                    rm_rf(symlink)
                else:
                    typer.echo("Cancelled.")
                    raise typer.Abort()
            venv.mkdir(parents=True, exist_ok=True)
            symlink.symlink_to(venv)
            proj.save_json_metadata_file()
            typer.echo(f"symlink created: {symlink} -> {venv}")


@app.command("ls")
def list_venvs(
    ctx: typer.Context,
    cache_root: Path | None = typer.Option(  # noqa: B008
        None,
        "--cache-root",
        help=(
            "Override the cache root directory "
            "(defaults to XDG_DATA_HOME/uvlink/cache)."
        ),
    ),
) -> None:
    """List status of existing projects."""

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
    cache_root: Path | None = typer.Option(  # noqa: B008
        None,
        "--cache-root",
        help=(
            "Override the cache root directory "
            "(defaults to XDG_DATA_HOME/uvlink/cache)."
        ),
    ),
) -> None:
    """Remove cached venvs whose projects are no longer linked."""

    ps = Projects(base_path=cache_root) if cache_root else Projects()
    link_infos = ps.get_list()
    for link_info in link_infos:
        if not link_info.is_linked:
            proj_cache = link_info.project.project_cache_dir
            if typer.confirm(f"Remove {proj_cache.as_posix()} ?", default=True):
                typer.secho(f"Removing {proj_cache.as_posix()}", fg="red")
                rm_rf(proj_cache)
            else:
                typer.echo(f"Skiped {proj_cache.as_posix()}")


if __name__ == "__main__":  # pragma: no cover - convenience execution
    app()
