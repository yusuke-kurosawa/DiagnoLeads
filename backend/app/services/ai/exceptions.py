"""
AI Service Custom Exceptions

Structured exceptions for better error handling and logging.
"""


class AIServiceError(Exception):
    """Base exception for AI service errors"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class AIAPIError(AIServiceError):
    """Exception raised when Claude API call fails"""

    pass


class AIRateLimitError(AIServiceError):
    """Exception raised when hitting API rate limits"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class AIValidationError(AIServiceError):
    """Exception raised when AI response validation fails"""

    pass


class AIJSONParseError(AIServiceError):
    """Exception raised when JSON parsing fails"""

    pass


class AIPromptInjectionError(AIServiceError):
    """Exception raised when potential prompt injection detected"""

    pass
