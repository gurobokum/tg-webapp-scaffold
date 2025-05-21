from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from dishka import Provider, Scope, from_context, make_async_container, provide
from dishka.integrations.base import wrap_injection
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat, Update

from app.core.errors import AppError
from app.tgbot.context import Context


class TGBotProvider(Provider):
    update = from_context(provides=Update, scope=Scope.REQUEST)
    context = from_context(provides=Context, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def db_session(self, context: Context) -> AsyncIterator[AsyncSession]:
        async with context.db_session_maker() as db_session:
            yield db_session

    @provide(scope=Scope.REQUEST)
    def chat(self, update: Update) -> Chat:
        chat = update.effective_chat
        if not chat:
            raise AppError("Chat is None")
        return chat


tg_container = make_async_container(TGBotProvider())


def inject(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    injected_func = wrap_injection(
        func=func,
        is_async=True,
        container_getter=lambda *_: tg_container,
        manage_scope=True,
        provide_context=provide_context,
    )

    return injected_func


def provide_context(args: tuple[Any, ...], _: dict[str, Any]) -> dict[Any, Any]:
    return {
        Update: args[0],
        Context: args[1],
    }
