class PromptLibError(Exception):
    """Base class for exceptions in this module."""
    pass

class PromptNotFoundError(PromptLibError):
    """Raised when a prompt is not found."""
    pass

class ValidationError(PromptLibError):
    """Raised when validation fails."""
    pass

class StorageError(PromptLibError):
    """Raised when a storage operation fails."""
    pass

class WorkflowError(PromptLibError):
    """Raised when a workflow operation fails."""
    pass

class PluginError(PromptLibError):
    """Raised when a plugin operation fails."""
    pass
