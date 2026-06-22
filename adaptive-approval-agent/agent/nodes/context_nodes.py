from agent.guardrails.card_rules import CardRulesEngine
from agent.guardrails.routing_rules import RoutingRulesEngine
from agent.paths import config_path
from agent.rendering.computed_attributes import apply_computed_attributes
from agent.rendering.field_registry import FieldRegistry


def fetch_context_node(state, agent):
    request = state["request"]
    context = agent.salesforce.fetch_context(request.source_record_id, request.raw_payload)
    state["context"] = context
    return state


def load_registry_and_rules_node(state, _agent):
    process = state["request"].process_type
    registry = FieldRegistry.from_file(config_path(process, "field-registry.json"))
    state["registry"] = registry
    state["context"] = apply_computed_attributes(registry, state["context"])
    state["routing_rules"] = RoutingRulesEngine.from_file(config_path(process, "routing-rules.yaml"))
    state["card_rules"] = CardRulesEngine.from_file(config_path(process, "card-rules.yaml"))
    return state
