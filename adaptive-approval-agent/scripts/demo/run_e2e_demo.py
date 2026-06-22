import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

BPMN_PROCESS_KEY = os.getenv("DEALDESK_BPMN_PROCESS_KEY", "DealDeskSolution.Agentic.DealDeskApproval:1.0.1981")
BPMN_RELEASE_KEY = os.getenv("DEALDESK_BPMN_RELEASE_KEY", "a9255f28-9c8d-492f-9e65-e10edf9a9d74")
# FOLDER_KEY is used to START the BPMN job (solution subfolder).
# Job STATUS/TRACES are tracked in the parent DealDesk folder.
FOLDER_KEY = os.getenv("DEALDESK_FOLDER_KEY", "1cafc99b-2d8a-40b5-a81b-429ec36e5522")
JOB_POLL_FOLDER_KEY = os.getenv("DEALDESK_JOB_POLL_FOLDER_KEY", "5f93aec0-a43b-4281-9fa4-0b695b23effe")

SCENARIOS = {
    "auto": "tests/fixtures/rpc_auto.json",
    "low": "tests/fixtures/rpc_8pct.json",
    "high": "tests/fixtures/rpc_30pct.json",
    "cfo": "tests/fixtures/rpc_high_value.json",
}

TERMINAL_STATES = {"Successful", "Failed", "Faulted"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run DealDesk BPMN E2E with scenario/fixture inputs.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario", choices=sorted(SCENARIOS.keys()))
    group.add_argument("--fixture", help="Path to fixture JSON file.")
    parser.add_argument("--poll-seconds", type=int, default=10, help="Polling interval.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=3600,
        help="Maximum total wait for terminal job state.",
    )
    return parser.parse_args()


def resolve_fixture_path(args: argparse.Namespace) -> Path:
    if args.scenario:
        return REPO_ROOT / SCENARIOS[args.scenario]
    return (REPO_ROOT / args.fixture).resolve()


def load_fixture(fixture_path: Path) -> dict[str, Any]:
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if "request" not in payload:
        raise ValueError("Fixture must contain top-level 'request'.")
    return payload


def extract_json(stdout_text: str) -> dict[str, Any]:
    start_idx = stdout_text.find("{")
    if start_idx < 0:
        raise ValueError(f"No JSON payload found in CLI output: {stdout_text}")
    return json.loads(stdout_text[start_idx:])


def run_cli(command: list[str]) -> dict[str, Any]:
    if sys.platform != "win32":
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
    else:
        quoted = subprocess.list2cmdline(command)
        proc = subprocess.run(
            ["cmd", "/c", quoted],
            capture_output=True,
            text=True,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(
            "CLI command failed:\n"
            f"Command: {' '.join(command)}\n"
            f"ExitCode: {proc.returncode}\n"
            f"STDOUT: {proc.stdout}\n"
            f"STDERR: {proc.stderr}"
        )
    return extract_json(proc.stdout)


def start_job(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if not BPMN_RELEASE_KEY:
        raise ValueError(
            "Missing BPMN release key. Set DEALDESK_BPMN_RELEASE_KEY env var before running."
        )

    bpm_inputs = {"request": payload["request"]}
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as temp_file:
        json.dump(bpm_inputs, temp_file, separators=(",", ":"))
        inputs_arg = f"@{temp_file.name}"

    command = [
        "uip",
        "maestro",
        "bpmn",
        "process",
        "run",
        BPMN_PROCESS_KEY,
        FOLDER_KEY,
        "--release-key",
        BPMN_RELEASE_KEY,
        "--inputs",
        inputs_arg,
        "--output",
        "json",
    ]
    result = run_cli(command)
    data = result.get("Data", {})
    job_key = data.get("jobKey")
    if not job_key:
        raise RuntimeError(f"Run response missing jobKey: {json.dumps(result, indent=2)}")
    return job_key, result


def get_job_status_from_traces(job_key: str) -> dict[str, Any]:
    """
    Use 'bpmn job traces' to get final job state.
    bpmn job status requires a folder key that doesn't work for solution subfolders;
    traces works without one and emits a terminal summary line.
    """
    import re as _re
    command = ["uip", "maestro", "bpmn", "job", "traces", job_key]
    try:
        if sys.platform == "win32":
            quoted = subprocess.list2cmdline(command)
            run_args = {"args": ["cmd", "/c", quoted]}
        else:
            run_args = {"args": command}
        proc = subprocess.run(
            **run_args,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = proc.stdout + proc.stderr
        # Traces emit a line like: Job <key> completed with state <State> (<ms>ms)
        match = _re.search(r"completed with state (\w+)", output)
        if match:
            return {"Result": "Success", "Data": {"state": match.group(1), "traces": output}}
        # If still running traces may not have a terminal line yet
        return {"Result": "Success", "Data": {"state": "Running", "traces": output}}
    except subprocess.TimeoutExpired:
        return {"Result": "Success", "Data": {"state": "Running"}}


def poll_until_terminal(job_key: str, poll_seconds: int, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    while True:
        status = get_job_status_from_traces(job_key)
        data = status.get("Data", {})
        state = data.get("state", "")
        elapsed = int(time.time() - started)
        print(f"[poll] job={job_key} state={state} elapsed={elapsed}s")

        if state in TERMINAL_STATES:
            return status

        if elapsed >= timeout_seconds:
            raise TimeoutError(
                f"Timed out waiting for terminal state after {timeout_seconds}s. Last state: {state}"
            )

        time.sleep(poll_seconds)


def print_checklist(state: str) -> None:
    print("\nManual checks:")
    print("- Action Center task creation for approval scenarios.")
    print("- WaitDecision logs include HITL create + email send + decision capture.")
    print("- Requester summary email delivered.")
    print("- Data Fabric ApprovalAudit record matches the scenario.")
    print(f"\nFinal state: {state}")


def main() -> None:
    args = parse_args()
    fixture_path = resolve_fixture_path(args)
    payload = load_fixture(fixture_path)

    print(f"Fixture: {fixture_path}")
    print(f"ProcessKey: {BPMN_PROCESS_KEY}")
    print(f"FolderKey: {FOLDER_KEY}")

    job_key, start_response = start_job(payload)
    print("\nStart response:")
    print(json.dumps(start_response, indent=2))
    print(f"\nJob key: {job_key}")

    final_status = poll_until_terminal(job_key, args.poll_seconds, args.timeout_seconds)
    print("\nFinal status:")
    print(json.dumps(final_status, indent=2))
    final_state = final_status.get("Data", {}).get("state", "Unknown")
    print_checklist(final_state)

    if final_state != "Successful":
        sys.exit(1)


if __name__ == "__main__":
    main()
