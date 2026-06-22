from pathlib import Path

import yaml

from agent.guardrails.engines import evaluate_condition


class RoutingRulesEngine:
    def __init__(self, hard_rules: list[dict], soft_guidance: list[dict]):
        self.hard_rules = hard_rules
        self.soft_guidance = soft_guidance

    @classmethod
    def from_file(cls, path: Path) -> "RoutingRulesEngine":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(raw.get("hard_rules", []), raw.get("soft_guidance", []))

    def validate(self, context: dict, roles: list[str]) -> list[str]:
        violations: list[str] = []
        for rule in self.hard_rules:
            cond = rule.get("when", {})
            field = cond.get("field")
            if evaluate_condition(context.get(field), cond.get("operator", "=="), cond.get("value")):
                required = rule.get("require_role")
                if required and required not in roles:
                    violations.append(f"Missing required role: {required}")
        return violations
