from fastapi import status

from app.core.http_errors import HTTPError


class HTTPInvalidInviteCodeError(HTTPError):
    detail = "Invalid invite code"
    status_code = status.HTTP_403_FORBIDDEN
