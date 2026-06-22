.PHONY: install lint format test test-unit test-int provision-dev provision-uat agent-package smoke-outlook

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run mypy agent setup-agent aggregate-analyzer

format:
	uv run ruff check . --fix
	uv run ruff format .

test test-unit:
	uv run pytest tests/unit/ -v

test-int:
	uv run pytest tests/integration/ -v --run-integration

provision-dev:
	uv run python -m orchestrator.provision --config orchestrator/config/dev.yaml

provision-uat:
	uv run python -m orchestrator.provision --config orchestrator/config/uat.yaml

agent-package:
	uv run uipath pack agent/

smoke-outlook:
	uv run python scripts/smoke/send_test_card.py
