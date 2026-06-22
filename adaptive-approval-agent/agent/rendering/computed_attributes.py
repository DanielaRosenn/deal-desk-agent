from typing import Any, Callable

ComputedFn = Callable[[Any, dict], Any]

COMPUTED_ATTRIBUTES: dict[str, ComputedFn] = {
    "is_above_threshold": lambda value, ctx: float(value) > 0.25 if value is not None else False,
    "is_above_value_threshold": lambda value, ctx: float(value) > 500000 if value is not None else False,
    "is_priority_customer": lambda value, ctx: ctx.get("deal.customer_segment")
    in ("enterprise", "strategic"),
}


def apply_computed_attributes(registry, context: dict) -> dict:
    enriched = dict(context)
    for field_id, field_def in registry.doc.fields.items():
        if not field_def.computed_attributes:
            continue
        raw_value = registry.fetch_value(field_id, context)
        for attr_name in field_def.computed_attributes:
            fn = COMPUTED_ATTRIBUTES.get(attr_name)
            if fn:
                enriched[f"{field_id}.{attr_name}"] = fn(raw_value, context)
    return enriched
