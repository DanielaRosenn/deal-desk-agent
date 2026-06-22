from agent.schemas.errors import TransientError


class BedrockClient:
    def __init__(self, settings):
        self.settings = settings

    def invoke(self, prompt: str, model: str, response_format=None):
        if not prompt:
            raise TransientError("Empty prompt")
        # Stub for deterministic local rebuild; replace with AWS Bedrock invocation in deployment env.
        return "{}"
