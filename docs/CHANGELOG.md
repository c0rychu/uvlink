# Changelog

Note: Trying to follow the essentials of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [SemVer](https://semver.org/spec/v2.0.0.html).

## 0.7.0

### Added
- `uvlink link [VENV_TYPE]` accepts an optional folder name so you can create links such as `.venv-prod` or `.pdm-venv` without extra commands.

### Changed
- `venv_type` input is now validated as a portable filename (no path separators, limited to alphanumerics plus `._-`, no trailing dots/spaces), preventing cache corruption from illegal names.

## 0.6.0

### Changed
- **Breaking:** Cache directories now include the virtualenv type in the folder name (for example `myapp-dr3ag8a41ro9-.venv/.venv`), allowing multiple venv types per project to be supported in the future without collisions. Remove old caches and rerun `uvlink link` to migrate.
- `uvlink ls` now displays the cache identifier with the environment type suffix, making it easier to see which cache belongs to which env flavor.

## 0.5.0

### Added
- Each cached project's `project.json` now records the uvlink version that created it, making it easier to audit caches after upgrades.

### Changed
- `uvlink ls` renders with a minimal table style so the listing is easier to read in plain terminals.

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
