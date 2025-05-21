from collections.abc import Coroutine
from functools import wraps
from typing import Any, Callable, cast, overload

from telegram import Update
from telegram.ext._utils.types import HandlerCallback

from app.auth.services import TGUserService
from app.core.errors import ForbiddenError, UserIsBlockedError
from app.tgbot.context import Context
from app.tgbot.utils import extract_user_data

TCallback = HandlerCallback[Update, Context, Any]


@overload
def requires_auth(func: TCallback) -> TCallback: ...


@overload
def requires_auth(*, is_admin: bool = False) -> Callable[[TCallback], TCallback]: ...


def requires_auth(
    *args: Any, **kwargs: Any
) -> TCallback | Callable[[TCallback], TCallback]:
    def _inner(is_admin: bool = False) -> Callable[[TCallback], TCallback]:
        def requires_auth(
            call: TCallback,
        ) -> TCallback:
            @wraps(call)
            async def wrapper(
                update: Update, context: Context, *args: Any, **kwargs: Any
            ) -> Any:
                if not context.db_session:
                    raise ValueError(
                        "DB session is None, please wrap handler with @db_session"
                    )

                user_data = extract_user_data(update)
                if not user_data:
                    raise ValueError("User data is None")

                tg_user_svc = TGUserService(context.db_session)
                tg_user = await tg_user_svc.get_user_and_update(user_data)
                if not tg_user:
                    raise ForbiddenError
                if tg_user.is_blocked:
                    raise UserIsBlockedError
                if is_admin and not tg_user.is_admin:
                    raise ForbiddenError("User is not admin")
                # TODO: swtich on dependency injection
                # https://github.com/reagento/dishka/issues/450
                context.tg_user = tg_user
                return await call(update, context, *args, **kwargs)

            return wrapper

        return requires_auth

    if len(args) == 1 and callable(args[0]):
        return _inner()(cast(TCallback, args[0]))
    return _inner(*args, **kwargs)


def db_session(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(func)
    async def wrapper(update: Update, context: Context, **kwargs: Any) -> Any:
        async with context.db_session_maker() as db_session:
            # TODO: swtich on dependency injection
            # https://github.com/reagento/dishka/issues/450
            context.db_session = db_session
            return await func(update, context, **kwargs)

    return wrapper
