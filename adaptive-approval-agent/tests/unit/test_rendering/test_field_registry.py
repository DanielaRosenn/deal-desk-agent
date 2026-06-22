from pathlib import Path

from agent.rendering.field_registry import FieldRegistry


def test_load_rpc_succeeds():
    registry = FieldRegistry.from_file(Path("configs/rpc/field-registry.json"))
    assert registry.process_type == "rpc"
