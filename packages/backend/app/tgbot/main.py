from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from arq.connections import create_pool
from telegram import BotCommand, Update

from app.conf import settings
from app.core.errors import ForbiddenError
from app.credits.handlers import handlers as credits_handlers
from app.db import AsyncSessionMaker
from app.tgbot.app import TGApp, tg_app
from app.tgbot.context import Context
from app.tgbot.handlers import TEXTS, handlers
from app.tgbot.utils import extract_user_data, get_texts
from app.worker.conf import WorkerSettings

logger = structlog.get_logger()


async def error_handler(update: object, context: Context) -> None:
    error = context.error
    # Show welcome message to user if he is not authorized
    if isinstance(error, ForbiddenError) and isinstance(update, Update):
        user_data = extract_user_data(update)
        if user_data:
            chat = update.effective_chat
            texts = get_texts(TEXTS, user_data.language_code)
            if chat:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=texts.start.welcome_text,
                )
    logger.exception("Exception while handling update:", exc_info=error)


@asynccontextmanager
async def start_tg_app(session_maker: AsyncSessionMaker) -> AsyncGenerator[TGApp, None]:
    tg_app.add_handlers(handlers)
    tg_app.add_handlers(credits_handlers)
    tg_app.add_error_handler(error_handler)
    if settings.TGBOT_SETUP_COMMANDS:
        await setup_commands(tg_app)
    if settings.TGBOT_WEBHOOK_URL and settings.TGBOT_WEBHOOK_SECRET_TOKEN:
        await tg_app.bot.set_webhook(
            settings.TGBOT_WEBHOOK_URL,
            secret_token=settings.TGBOT_WEBHOOK_SECRET_TOKEN.get_secret_value(),
        )
        logger.info(f"Telegram webhook is set as {settings.TGBOT_WEBHOOK_URL}")

    Context.db_session_maker = session_maker
    Context.arq = await create_pool(
        WorkerSettings.redis_settings, default_queue_name=WorkerSettings.queue_name
    )

    async with tg_app:
        if tg_app.post_init is not None:
            await tg_app.post_init(tg_app)

        if tg_app.updater is not None:
            await tg_app.updater.start_polling()
            logger.info("Telegram bot polling started")

        await tg_app.start()
        logger.info("Telegram bot started")

        yield tg_app

        await Context.arq.aclose()
        if tg_app.updater is not None:
            await tg_app.updater.stop()
        await tg_app.stop()
        if tg_app.post_stop is not None:
            await tg_app.post_stop(tg_app)
    if tg_app.post_shutdown is not None:
        await tg_app.post_shutdown(tg_app)


async def setup_commands(tg_app: TGApp) -> None:
    commands = {
        "en": {
            "start": "start",
        },
        "ru": {
            "start": "старт",
        },
    }
    # localize
    for lang in ["en", "ru"]:
        commands_lang = commands[lang]
        await tg_app.bot.set_my_commands(
            [BotCommand(k, v) for k, v in commands_lang.items()],
            language_code=lang,
        )
