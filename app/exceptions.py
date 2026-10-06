class AppError(Exception):
    status_code = 400
    detail = "Bad request"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Not found"


class ConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class PermissionDeniedError(AppError):
    status_code = 403
    detail = "You do not have permission to do this"


class AuthenticationError(AppError):
    status_code = 401
    detail = "Could not validate credentials"


class BusinessRuleError(AppError):
    status_code = 422
    detail = "Request breaks a business rule"


class EmailAlreadyExistsError(ConflictError):
    detail = "A user with this email already exists"

    def __init__(self, email: str):
        self.email = email
        super().__init__()


class LoginFailedError(AuthenticationError):
    detail = "Incorrect email or password"