from pathlib import Path
import hashlib


def hash_path(path: str | Path, length: int = 12) -> str:
    """Generate a deterministic short hash for a filesystem path.

    Args:
        path: Filesystem path to hash; may be relative.
        length: Number of leading hexadecimal characters to
            return from the SHA-256 digest. Defaults to 12.

    Returns:
        str: Prefix of the SHA-256 hash for the resolved absolute path.
    """
    abs_path = Path(path).resolve().as_posix()
    abs_path_hash = hashlib.sha256(abs_path.encode("utf-8")).hexdigest()
    return abs_path_hash[:length]
