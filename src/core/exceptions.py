class AppException(Exception):
    """Base exception class for application exceptions."""
    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str = None, status_code: int = None, error_code: str = None):
        self.message = message or "An unexpected error occurred"
        self.status_code = status_code or self.__class__.status_code
        self.error_code = error_code or self.__class__.error_code
        super().__init__(self.message)


class DatabaseError(AppException):
    """Exception raised for database errors."""
    status_code = 500
    error_code = "database_error"


class RepositoryError(AppException):
    """Exception raised for repository errors."""
    status_code = 500
    error_code = "repository_error"


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""
    status_code = 404
    error_code = "not_found"


class ValidationError(AppException):
    """Exception raised for validation errors."""
    status_code = 400
    error_code = "validation_error"


class BusinessError(AppException):
    """Exception raised for business logic errors."""
    status_code = 400
    error_code = "business_error"


class AuthenticationError(AppException):
    """Exception raised for authentication errors."""
    status_code = 401
    error_code = "authentication_error"


class AuthorizationError(AppException):
    """Exception raised for authorization errors."""
    status_code = 403
    error_code = "authorization_error"


class ConfigurationError(AppException):
    """Exception raised for configuration errors."""
    status_code = 500
    error_code = "configuration_error"
