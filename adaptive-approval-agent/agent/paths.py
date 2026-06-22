from pathlib import Path

_AGENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _AGENT_DIR.parent


def config_path(process_type: str, file_name: str) -> Path:
    """Resolve a process config file.

    Prefers the copy bundled inside the agent package (so it survives packaging),
    and falls back to the repo-root ``configs/`` tree for local development.
    """
    candidates = [
        _AGENT_DIR / "configs" / process_type / file_name,
        _REPO_ROOT / "configs" / process_type / file_name,
        Path("configs") / process_type / file_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def template_dir() -> Path:
    """Adaptive-card scaffold directory, resolved relative to the package."""
    candidates = [
        _AGENT_DIR / "templates" / "outlook",
        Path("agent") / "templates" / "outlook",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
