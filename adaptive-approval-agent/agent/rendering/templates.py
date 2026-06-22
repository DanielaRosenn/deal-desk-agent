import json
from pathlib import Path


def load_scaffold(base_dir: Path, persona: str) -> dict:
    path = base_dir / f"{persona}.json"
    if not path.exists():
        path = base_dir / "safe_mode.json"
    return json.loads(path.read_text(encoding="utf-8"))
