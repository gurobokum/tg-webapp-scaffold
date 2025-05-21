from typing import Any


class AppError(Exception):
    def __init__(
        self, message: str | None = None, code: int | str | None = None, **kwargs: Any
    ) -> None:
        if message is None:
            message = self.__class__.__name__
        super().__init__(message)
        self.message = message
        self.code = code
        self.kwargs = kwargs or {}


class LockedError(AppError):
    message = "Locked"


class NotFoundError(AppError):
    message = "Not found"
    code = 404


class ForbiddenError(AppError):
    message = "Forbidden"
    code = 403


class UserIsBlockedError(AppError):
    message = "User is blocked"
    code = "user_blocked"
