class AdaptiveApprovalError(Exception):
    pass


class TransientError(AdaptiveApprovalError):
    pass


class PermanentError(AdaptiveApprovalError):
    pass


class GuardrailViolation(PermanentError):
    pass


class FieldRegistryError(PermanentError):
    pass


class RenderingError(PermanentError):
    pass


class SecurityError(PermanentError):
    pass
