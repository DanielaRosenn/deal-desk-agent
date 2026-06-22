import os
from dataclasses import dataclass, field


@dataclass
class AgentSettings:
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    planner_model: str = field(default_factory=lambda: os.getenv("BEDROCK_PLANNER_MODEL", "anthropic.claude-3-5-sonnet"))
    renderer_model: str = field(default_factory=lambda: os.getenv("BEDROCK_RENDERER_MODEL", "anthropic.claude-3-5-sonnet"))
    response_model: str = field(default_factory=lambda: os.getenv("BEDROCK_RESPONSE_MODEL", "anthropic.claude-3-5-sonnet"))
    callback_url: str = field(default_factory=lambda: os.getenv("CALLBACK_URL", "https://example.com/callback"))
    outlook_originator_guid: str = field(default_factory=lambda: os.getenv("OAM_PROVIDER_GUID", "00000000-0000-0000-0000-000000000000"))
    outlook_connection_key: str = field(default_factory=lambda: os.getenv("OUTLOOK_CONNECTION_KEY", "outlook-approval"))
    manager_resolver: str = field(default_factory=lambda: os.getenv("MANAGER_RESOLVER", "hibob"))
    input_bucket_name: str = field(default_factory=lambda: os.getenv("DEAL_INPUT_BUCKET", "DealDeskInputs"))
    input_bucket_folder: str = field(default_factory=lambda: os.getenv("DEAL_INPUT_FOLDER", "DealDesk"))
    input_blob_path: str = field(default_factory=lambda: os.getenv("DEAL_INPUT_BLOB", "deal-input.json"))
