"""uvlink command-line interface powered by Typer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from uvlink.project import Project, Projects, rm_rf

app = typer.Typer(
    help="Create .venv in global cache and symlink back.", no_args_is_help=True
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    project_dir: Optional[Path] = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-p",
        show_default=True,
        dir_okay=True,
        file_okay=False,
        writable=True,
        resolve_path=True,
        help="Path to the project root; defaults to the current working directory.",
    ),
    dry_run: Optional[bool] = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
) -> None:
    ctx.obj = {
        "dry_run": dry_run,
        "proj": Project(project_dir=project_dir),
    }


@app.command()
def link(
    ctx: typer.Context,
    dry_run: Optional[bool] = typer.Option(
        False, "--dry-run", help="Show what would be executed without actually run it."
    ),
) -> None:
    """Create (or update) the hidden project symlink pointing at the cached venv."""
    proj = ctx.obj["proj"]
    dry_run = dry_run or ctx.obj["dry_run"]
    if dry_run:
        symlink = proj.project_dir / f".{proj.venv_type}"
        venv = proj.project_cache_dir / f"{proj.venv_type}"
        typer.echo(f"ln -s {venv} {symlink}")
        typer.Exit()

    else:
        if proj.venv_type in {"venv"}:
            hidden = True
        else:
            hidden = False
            raise NotImplementedError(
                f"venv_type = {proj.venv_type} not supported (yet)"
            )

        if not proj.project_dir.is_dir():
            raise NotADirectoryError(f"{proj.project_dir} is not a directory")
        else:
            if hidden:
                symlink = proj.project_dir / f".{proj.venv_type}"
                venv = proj.project_cache_dir / f"{proj.venv_type}"
            else:
                symlink = proj.project_dir / f"{proj.venv_type}"
                venv = proj.project_cache_dir / f"{proj.venv_type}"
            if venv.exists() or venv.is_symlink():
                if typer.confirm(f"'{venv}' already exist, remove?", default=True):
                    typer.echo("Removing...")
                    rm_rf(venv)
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


@app.command()
def list(ctx: typer.Context) -> None:
    """List status of existing projects"""

    ps = Projects()
    linked = ps.get_list()
    table = Table()

    table.add_column("Cache", no_wrap=True)
    table.add_column("Project Path")
    table.add_column("Is Linked")

    for row in linked:
        table.add_row(
            row.project_name_hash,
            row.project_dir_str,
            "✅" if row.is_linked else "❌",
        )
    console.print(table)


if __name__ == "__main__":  # pragma: no cover - convenience execution
    app()
