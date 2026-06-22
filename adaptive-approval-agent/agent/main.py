"""Agent entrypoint module.

Exports three compiled LangGraph StateGraphs for the UiPath LangGraph runtime
(declared in langgraph.json), plus the legacy plain-function wrappers kept for
backward-compatible invocation.

IMPORTANT: No auth-dependent clients are instantiated at module level.
           All UiPath/LLM clients are created inside graph nodes.
"""

import os
import sys
import types

# When packaged by `uipath pack`, the `agent/` directory is flattened to the
# package root.  Register a synthetic `agent` package pointing here so that
# every `agent.<module>` import resolves correctly.  No-op in local dev.
if "agent" not in sys.modules:
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    _pkg = types.ModuleType("agent")
    _pkg.__path__ = [_here]
    sys.modules["agent"] = _pkg

from agent.graphs.plan_graph import build_plan_graph
from agent.graphs.render_graph import build_render_graph
from agent.graphs.response_graph import build_response_graph

# ---------------------------------------------------------------------------
# Compiled LangGraph graphs - declared in langgraph.json
# ---------------------------------------------------------------------------

plan_graph = build_plan_graph()
render_graph = build_render_graph()
response_graph = build_response_graph()
