import json
import shutil
import subprocess
from pathlib import Path


def validate_flow(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return [f"{path}: invalid json ({exc})"]
    for key in ("name", "version", "nodes", "edges"):
        if key not in data:
            errors.append(f"{path}: missing {key}")
    return errors


def main() -> None:
    flow_files = list(Path("AdaptiveApprovalSolution").rglob("*.flow"))
    all_errors: list[str] = []
    uip_bin = shutil.which("uip")
    for flow in flow_files:
        all_errors.extend(validate_flow(flow))
        if uip_bin:
            cli_check = subprocess.run(
                [uip_bin, "flow", "validate", str(flow), "--output", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            if cli_check.returncode != 0:
                all_errors.append(f"{flow}: cli validation failed: {cli_check.stdout or cli_check.stderr}")
    if all_errors:
        raise SystemExit("\n".join(all_errors))
    print(f"Validated {len(flow_files)} flow files")


if __name__ == "__main__":
    main()
