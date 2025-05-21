from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str
    status_code: int


class HTTPUnauthorizedError(HTTPError): ...


class HTTPNotFoundError(HTTPError): ...


class HTTPForbiddenError(HTTPError): ...
