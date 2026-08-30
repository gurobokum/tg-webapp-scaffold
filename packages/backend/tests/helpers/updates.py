from typing import Any

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, ExtBot

from app.db import AsyncSessionMaker
from app.tgbot.context import Context


def make_update(
    bot: ExtBot[None],
    *,
    text: str = "/start",
    user_id: int = 1001,
    chat_id: int | None = None,
    language_code: str = "en",
) -> Update:
    chat_id = chat_id if chat_id is not None else user_id
    entities: list[dict[str, Any]] = []
    if text.startswith("/"):
        entities.append(
            {"type": "bot_command", "offset": 0, "length": len(text.split()[0])}
        )
    return Update.de_json(
        {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "date": 1,
                "chat": {"id": chat_id, "type": "private"},
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": f"testuser{user_id}",
                    "language_code": language_code,
                },
                "text": text,
                "entities": entities,
            },
        },
        bot,
    )


def make_context(bot: ExtBot[None], db_session_maker: AsyncSessionMaker) -> Context:
    application: Application[
        ExtBot[None], Context, dict[Any, Any], dict[Any, Any], dict[Any, Any], Any
    ] = (
        ApplicationBuilder()
        .bot(bot)
        .updater(None)
        .context_types(ContextTypes(context=Context))
        .build()
    )
    context = Context(application=application)
    context.db_session_maker = db_session_maker
    return context
