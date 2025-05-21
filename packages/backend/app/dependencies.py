import hashlib
import hmac
import json
import re
from typing import Annotated
from urllib.parse import unquote

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.auth.models import TGUser
from app.auth.services import TGUserService
from app.conf import settings
from app.tgbot.schemas import UserTGData


async def validate_init_data(
    auth_key: Annotated[str, Depends(APIKeyHeader(name="x-telegram-auth"))],
) -> None:
    m = re.compile(r"^((.*?)&hash=(.*?))$").match(unquote(auth_key))
    if not m:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication credentials"
        )

    init_data = m.group(1)
    data_hash = m.group(3)
    data = {
        k: v for (k, v) in [p.split("=") for p in init_data.split("&")] if k != "hash"
    }
    data_check_string = "\n".join([f"{k}={data[k]}" for k in sorted(data.keys())])

    secret_key = hmac.new(
        b"WebAppData", settings.TGBOT_TOKEN.get_secret_value().encode(), hashlib.sha256
    ).digest()
    result_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if result_hash != data_hash:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Hash is not valid")


async def get_user_or_create_with_tg_data(
    auth_key: Annotated[str, Depends(APIKeyHeader(name="x-telegram-auth"))],
    tg_user_svc: Annotated[TGUserService, Depends(TGUserService.inject)],
) -> TGUser:
    """
    WARNING: Data is trusted and should be validated before calling this function
    TODO: validate here one more time
    """
    m = re.compile(r"^((.*?)&hash=(.*?))$").match(unquote(auth_key))
    if not m:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication credentials"
        )

    init_data = m.group(1)
    data = {k: v for (k, v) in [p.split("=") for p in init_data.split("&")]}
    user_tg_data = UserTGData.model_validate(json.loads(data["user"]))
    tg_user = await tg_user_svc.get_user_and_update(user_tg_data)
    if not tg_user:
        if settings.TGBOT_REQUIRES_INVITE:
            # TODO: needs to be improved
            # with custom error middleware
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Signup without invite code is not allowed",
            )
        tg_user = await tg_user_svc.create(user_tg_data)
    return tg_user


AuthUser = Annotated[TGUser, Depends(get_user_or_create_with_tg_data)]
