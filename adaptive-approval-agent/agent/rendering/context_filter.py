from agent.rendering.field_registry import FieldRegistry


def filter_context_by_sensitivity(context: dict, registry: FieldRegistry, persona: str) -> dict:
    visible_ids = set(registry.ids_for_persona(persona))
    filtered = {}
    for field_id in visible_ids:
        filtered[field_id] = registry.fetch_value(field_id, context)
    return filtered
