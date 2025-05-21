from uuid import UUID

import structlog
from telegram import Bot
from telegram.constants import ParseMode

from app.conf import settings
from app.worker.conf import JobContext, task

logger = structlog.get_logger()


@task("task_example")
async def task_example(ctx: JobContext, from_chat_id: int) -> None:
    await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
        from_chat_id, "Hello!", parse_mode=ParseMode.HTML
    )
