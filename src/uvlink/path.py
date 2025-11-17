import hashlib
import json
import os
from pathlib import Path


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

    def __init__(self, project_dir: str | Path | None = None, venv_type: str = "venv"):
        """Initialize project metadata from the filesystem.

        Args:
            project_dir: Path to the project root; defaults to the current
                working directory.
            venv_type: Virtual environment strategy. Only ``"venv"`` is
                supported at the moment.

        Raises:
            NotImplementedError: If an unsupported ``venv_type`` is supplied.
        """

        self.project_dir = Path(project_dir or Path.cwd()).expanduser().resolve()
        self.project_hash = self.hash_path(self.project_dir)
        self.project_name = self.project_dir.name
        if venv_type in {"venv"}:
            self.venv_type = venv_type
        else:
            raise NotImplementedError(f"venv_type = {venv_type} not supported (yet)")
        self.project_cache_dir = (
            get_uvlink_dir("cache", self.venv_type)
            / f"{self.project_name}-{self.project_hash}"
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
