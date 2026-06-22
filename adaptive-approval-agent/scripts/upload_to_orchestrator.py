import json
import subprocess
from pathlib import Path


def run(cmd: list[str], dry_run: bool) -> dict:
    if dry_run:
        return {"status": "planned", "command": " ".join(cmd)}
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "command": " ".join(cmd),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    package = Path("AdaptiveApprovalSolution/dist/AdaptiveApprovalSolution.zip/AdaptiveApprovalSolution_1.0.0.zip")
    output = {
        "package_exists": package.exists(),
        "steps": [
            run(["uip", "solution", "upload", "AdaptiveApprovalSolution/AdaptiveApprovalSolution.uipx", "--output", "json"], args.dry_run),
            run(["uip", "solution", "publish", str(package), "--output", "json"], args.dry_run),
        ],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
