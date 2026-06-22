import json
from pathlib import Path


def format_prompt(name: str, **kwargs) -> str:
    prompt_file = Path(__file__).parent / f"{name}.txt"
    template = prompt_file.read_text(encoding="utf-8")
    return template.format(**kwargs)


def schema_json(model) -> str:
    return json.dumps(model.model_json_schema(), indent=2, sort_keys=True)


def pretty_json(payload) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, default=str)
