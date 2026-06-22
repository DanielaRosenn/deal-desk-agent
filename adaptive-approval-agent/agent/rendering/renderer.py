from pathlib import Path

from agent.rendering.field_registry import FieldRegistry
from agent.rendering.safe_mode import build_safe_mode_card
from agent.rendering.templates import load_scaffold
from agent.rendering.validators import validate_adaptive_card
from agent.schemas import CardSpec


class CardRenderer:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir

    def render(self, spec: CardSpec, context: dict, registry: FieldRegistry) -> dict:
        try:
            card = load_scaffold(self.template_dir, spec.approver_persona)
            fields = []
            for field_id in spec.primary_field_ids + spec.expandable_field_ids:
                value = registry.fetch_value(field_id, context)
                fields.append(
                    {
                        "type": "TextBlock",
                        "text": f"{registry.get(field_id).label if registry.get(field_id) else field_id}: "
                        f"{registry.format_value(field_id, value)}",
                        "wrap": True,
                    }
                )
            card.setdefault("body", [])
            card["body"] = [{"type": "TextBlock", "weight": "Bolder", "text": spec.headline}] + card["body"] + fields
            validate_adaptive_card(card)
            return card
        except Exception as exc:
            return build_safe_mode_card(spec.approval_id, str(exc))
