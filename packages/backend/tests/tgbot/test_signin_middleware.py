from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ApplicationHandlerStop,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

from app.auth.services import TGUserService
from app.core.errors import UserIsBannedError
from app.db import AsyncSessionMaker
from app.tgbot.context import Context
from app.tgbot.handlers import signin_middleware
from app.tgbot.i18n import TEXTS
from app.tgbot.main import error_handler
from app.tgbot.schemas import UserTGData
from tests.helpers.bot import bot_calls, make_offline_bot
from tests.helpers.updates import make_context, make_update

type PipelineApp = Application[
    ExtBot[None], Context, dict[Any, Any], dict[Any, Any], dict[Any, Any], None
]


async def make_pipeline_app(
    bot: ExtBot[None],
    db_session_maker: AsyncSessionMaker,
    probe: Callable[[Update, Context], Coroutine[Any, Any, None]],
) -> PipelineApp:
    Context.db_session_maker = db_session_maker
    app: PipelineApp = (
        ApplicationBuilder()
        .bot(bot)
        .updater(None)
        .job_queue(None)
        .context_types(ContextTypes(context=Context))
        .build()
    )
    app.add_handler(TypeHandler(Update, signin_middleware), group=-1)
    app.add_handler(TypeHandler(Update, probe))
    app.add_error_handler(error_handler)
    await app.initialize()
    return app


async def test_banned_user_update_stops_all_handlers(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        await user_svc.create(UserTGData.model_validate({"id": 7007}))
        await user_svc.update_user(7007, is_banned=True)

    triggered: list[int] = []

    async def probe(update: Update, context: Context) -> None:
        triggered.append(update.update_id)

    bot = await make_offline_bot()
    app = await make_pipeline_app(bot, db_session_maker, probe)
    try:
        await app.process_update(make_update(bot, user_id=7007, language_code="en"))
    finally:
        await app.shutdown()
        del Context.db_session_maker

    assert triggered == []
    sent = [p for e, p in bot_calls(bot) if e == "sendMessage"]
    assert [p["text"] for p in sent] == [TEXTS.en.error_handler.banned_text]


async def test_regular_user_update_reaches_handlers(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        await TGUserService(session).create(UserTGData.model_validate({"id": 8008}))

    triggered: list[int] = []

    async def probe(update: Update, context: Context) -> None:
        triggered.append(update.update_id)

    bot = await make_offline_bot()
    app = await make_pipeline_app(bot, db_session_maker, probe)
    try:
        await app.process_update(make_update(bot, user_id=8008))
    finally:
        await app.shutdown()
        del Context.db_session_maker

    assert triggered == [1]
    assert not [e for e, _ in bot_calls(bot) if e == "sendMessage"]


async def test_middleware_drops_admin_blocked_updates(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        await user_svc.create(UserTGData.model_validate({"id": 4004}))
        await user_svc.update_user(4004, is_banned=True)

    bot = await make_offline_bot()
    update = make_update(bot, user_id=4004)
    context = make_context(bot, db_session_maker)

    with pytest.raises(UserIsBannedError):
        await signin_middleware(update, context)


async def test_error_handler_responds_to_banned_user(
    db_session_maker: AsyncSessionMaker,
) -> None:
    bot = await make_offline_bot()
    update = make_update(bot, user_id=4004, language_code="en")
    context = make_context(bot, db_session_maker)
    context.error = UserIsBannedError()

    with pytest.raises(ApplicationHandlerStop):
        await error_handler(update, context)

    endpoint, params = bot_calls(bot)[-1]
    assert endpoint == "sendMessage"
    assert params["text"] == TEXTS.en.error_handler.banned_text


async def test_middleware_unblocks_returning_bot_blocked_user(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        await user_svc.create(UserTGData.model_validate({"id": 3003}))
        assert await user_svc.mark_bot_blocked(3003) is True

    bot = await make_offline_bot()
    update = make_update(bot, user_id=3003, language_code="en")
    context = make_context(bot, db_session_maker)

    await signin_middleware(update, context)

    async with db_session_maker() as session:
        user = await TGUserService(session).get_user(3003)
    assert user is not None
    assert user.is_bot_blocked is False
