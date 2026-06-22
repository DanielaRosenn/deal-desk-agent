from pathlib import Path

from agent.guardrails.routing_rules import RoutingRulesEngine


def test_routing_rules_validate():
    engine = RoutingRulesEngine.from_file(Path("configs/rpc/routing-rules.yaml"))
    violations = engine.validate({"deal.discount_pct": 0.3}, ["manager"])
    assert violations
