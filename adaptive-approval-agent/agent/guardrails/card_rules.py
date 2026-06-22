from pathlib import Path

import yaml

from agent.schemas import CardSpec


class CardRulesEngine:
    def __init__(self, personas: dict):
        self.personas = personas

    @classmethod
    def from_file(cls, path: Path) -> "CardRulesEngine":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(raw.get("personas", {}))

    def enforce(self, spec: CardSpec) -> tuple[CardSpec, list[str]]:
        corrections: list[str] = []
        limits = self.personas.get(spec.approver_persona, {})
        max_primary = limits.get("max_primary", 6)
        max_expandable = limits.get("max_expandable", 10)
        if len(spec.primary_field_ids) > max_primary:
            spec.primary_field_ids = spec.primary_field_ids[:max_primary]
            corrections.append("Trimmed primary fields to persona limit")
        if len(spec.expandable_field_ids) > max_expandable:
            spec.expandable_field_ids = spec.expandable_field_ids[:max_expandable]
            corrections.append("Trimmed expandable fields to persona limit")
        return spec, corrections
