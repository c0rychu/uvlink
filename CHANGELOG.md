# Changelog

Note: Trying to follow the essentials of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [SemVer](https://semver.org/spec/v2.0.0.html).

## 0.4.1

### Added
- `uvlink --version` / `uvlink -V` flag prints the installed tool version and exits.

### Changed
- CLI help banner now shows the current uvlink version for quick reference.

## 0.4.0

### Changed
- **Breaking:** Restructured cache directory from `~/.local/share/uvlink/cache/venv/<project>-<hash>/venv` to `~/.local/share/uvlink/cache/<project>-<hash>/.venv`. Existing caches created with prior versions should be deleted and recreated.
- Simplified symlink creation—removed unnecessary hidden-folder logic.

## 0.3.0

### Added
- `uvlink gc` command to clean up orphaned cache entries.
- `uvlink ls` command to list the linking status of venvs.

## 0.2.0

### Added
- Initial public release of `uvlink`
- `link` command to create the cache of venv in the `~/.local/share/uvlink/cache/...` directory and create symlinks `.venv` in the original project dir pointing to the cached venv.
- Documentation covering installation via `uv tool` and `pip`, along with guidance for typical usage patterns.
