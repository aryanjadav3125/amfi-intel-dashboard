class PipelineError(Exception):
    """Base exception for pipeline executions."""
    pass

class PipelineValidationError(PipelineError):
    """Raised when record fails cross-field validation checks."""
    pass

class PipelineRunError(PipelineError):
    """Raised when the execution run encounters critical failures."""
    pass
