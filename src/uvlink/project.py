import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import __version__


def rm_rf(path: Path) -> None:
    """Remove a filesystem path whether it's a file, symlink, or directory.

    Args:
        path (Path): Filesystem target to delete recursively.
    """

    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def get_uvlink_dir(*subpaths: str | Path) -> Path:
    """Return the uvlink data directory, optionally nested under subpaths.

    Args:
        *subpaths: Optional relative paths appended under the uvlink data root.

    Returns:
        Path: Absolute path to the uvlink data directory or provided subpath.
    """
    base = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    root = base / "uvlink"
    for sp in subpaths:
        root /= Path(sp)
    return root


class Project:
    """Encapsulate derived paths for a uvlink-managed project.

    Attributes:
        project_dir: Absolute project path resolved from the provided location.
        project_name: Final path component used to label cache directories.
        project_hash: Stable hash of ``project_dir`` to avoid collisions.
        project_cache_dir: Target directory under ``~/.local/share/uvlink``.
        venv_type: Virtual environment flavor (currently only ``venv``).
    """

    __slots__ = (
        "project_dir",
        "project_name",
        "project_hash",
        "project_cache_dir",
        "venv_type",
    )

    def __init__(self, project_dir: str | Path | None = None, venv_type: str = ".venv"):
        """Initialize project metadata from the filesystem.

        Args:
            project_dir: Path to the project root; defaults to the current
                working directory.
            venv_type: Virtual environment strategy. Only ``".venv"`` is
                supported at the moment.

        Raises:
            NotImplementedError: If an unsupported ``venv_type`` is supplied.
        """

        self.project_dir = Path(project_dir or Path.cwd()).expanduser().resolve()
        self.project_hash = self.hash_path(self.project_dir)
        self.project_name = self.project_dir.name
        if venv_type in {".venv"}:
            self.venv_type = venv_type
        else:
            raise NotImplementedError(f"venv_type = {venv_type} not supported (yet)")
        self.project_cache_dir = (
            get_uvlink_dir("cache") / f"{self.project_name}-{self.project_hash}"
        )

    @classmethod
    def from_json(cls, json_metadata_file: str | Path):
        """Hydrate a ``Project`` from a JSON metadata file.

        Args:
            json_metadata_file: Path to ``project.json``

        Returns:
            Project: Instance configured using the stored metadata.

        Raises:
            FileNotFoundError: If ``json_metadata_file`` does not exist.
        """

        pf = Path(json_metadata_file)
        if pf.exists():
            data = json.loads(pf.read_text())
        else:
            raise FileNotFoundError(f"{json_metadata_file} not found.")
        return cls(project_dir=data["project_dir"], venv_type=data["venv_type"])

    @staticmethod
    def hash_path(path: str | Path, length: int = 12) -> str:
        """Generate a deterministic short hash for a filesystem path.

        Args:
            path: Filesystem path to hash; may be relative.
            length: Number of leading hexadecimal characters to
                return from the SHA-256 digest. Defaults to 12.

        Returns:
            str: Prefix of the SHA-256 hash for the resolved absolute path.
        """
        abs_path = Path(path).expanduser().resolve().as_posix()
        abs_path_hash = hashlib.sha256(abs_path.encode("utf-8")).hexdigest()
        return abs_path_hash[:length]

    def save_json_metadata_file(self) -> Path:
        """Persist project metadata to ``project.json`` inside the cache dir.

        Returns:
            Path: Location of the written metadata file.
        """

        metadata = {
            "project_dir": self.project_dir.as_posix(),
            "project_name": self.project_name,
            "project_hash": self.project_hash,
            "venv_type": self.venv_type,
            "uvlink_version": __version__,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        metadata_path = self.project_cache_dir / "project.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        return metadata_path


@dataclass(slots=True)
class ProjectLinkInfo:
    """Snapshot describing whether a cached project is currently linked."""

    project: Project
    project_name_hash: str
    project_dir_str: str
    is_linked: bool


class Projects(list[Project]):
    """Iterable helper that discovers cached projects and their link status."""

    # TODO: do not hard coded "venv" here
    def __init__(
        self,
        base_path: str | Path = get_uvlink_dir("cache"),  # noqa: B008
    ):
        """Load every ``project.json`` nested directly under ``base_path``.

        Args:
            base_path: Directory that stores cached project folders.
        """

        self.base_path = Path(base_path)
        for file in self.base_path.glob("*/project.json"):
            self.append(Project.from_json(file))

    def get_list(self) -> list[ProjectLinkInfo]:
        """Return link information for each discovered project.

        Returns:
            list[ProjectLinkInfo]: One entry per cached project, detailing
                whether its ``.venv`` symlink currently targets uvlink's cache.
        """

        linked: list[ProjectLinkInfo] = []
        for p in self:
            symlink = p.project_dir / ".venv"  # TODO: do not hard code ".venv" here
            is_linked = (
                symlink.is_symlink() and symlink.resolve().parent == p.project_cache_dir
            )
            linked.append(
                ProjectLinkInfo(
                    project=p,
                    project_name_hash=f"{p.project_name}-{p.project_hash}",
                    project_dir_str=p.project_dir.as_posix(),
                    is_linked=is_linked,
                )
            )
        return linked
