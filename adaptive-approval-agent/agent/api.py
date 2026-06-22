import asyncio

from agent.graphs.plan_graph import build_plan_graph
from agent.graphs.render_graph import build_render_graph
from agent.graphs.response_graph import build_response_graph
from agent.integrations.bedrock import BedrockClient
from agent.integrations.data_service import DataServiceClient
from agent.integrations.manager_resolver import build_manager_resolver
from agent.integrations.salesforce import SalesforceClient


class AdaptiveApprovalAgent:
    def __init__(self, settings):
        self.settings = settings
        self.bedrock = BedrockClient(settings)
        self.salesforce = SalesforceClient(settings)
        self.manager_resolver = build_manager_resolver(settings)
        self.data_service = DataServiceClient(settings)
        self._plan_graph = build_plan_graph()
        self._render_graph = build_render_graph()
        self._response_graph = build_response_graph()

    @staticmethod
    def _as_dict(value):
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        return value

    @staticmethod
    def _invoke(graph, payload):
        return asyncio.run(graph.ainvoke(payload))

    def plan(self, request):
        from agent.schemas import RoutingPlan

        state = self._invoke(
            self._plan_graph,
            {
                "input_payload": {
                    "request": self._as_dict(request),
                }
            }
        )
        return RoutingPlan.model_validate(
            {
                "approvers": state["approvers"],
                "rationale": state["rationale"],
                "disposition": state["disposition"],
                "risk_score": state["risk_score"],
                "recommended_decision": state["recommended_decision"],
                "recommendation_rationale": state["recommendation_rationale"],
                "guardrail_violations_corrected": state["guardrail_violations_corrected"],
            }
        )

    def render(self, request, approver, history):
        state = self._invoke(
            self._render_graph,
            {
                "request": self._as_dict(request),
                "approver": self._as_dict(approver),
                "history": history,
            }
        )
        return state["rendered_card"]

    def process_response(self, request, routing_plan, current_approver_index, response, history):
        from agent.schemas import DecisionOutcome

        state = self._response_graph.invoke(
            {
                "request": self._as_dict(request),
                "routing_plan": self._as_dict(routing_plan),
                "current_approver_index": current_approver_index,
                "response": self._as_dict(response),
                "history": history,
            }
        )
        return DecisionOutcome.model_validate(
            {
                "next_action": state["next_action_out"],
                "next_approver": state["next_approver"],
                "completion_summary": state["completion_summary"],
                "escalation_reason": state["escalation_reason"],
                "info_request_message": state["info_request_message"],
                "learning_signals": state["learning_signals_out"],
            }
        )
