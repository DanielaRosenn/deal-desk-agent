from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from agent.schemas.errors import TransientError


retry_transient = retry(
    retry=retry_if_exception_type(TransientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
