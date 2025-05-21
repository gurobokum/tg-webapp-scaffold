from typing import Any

from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    ExtBot,
)

from app.conf import settings
from app.tgbot.context import Context

TGApp = Application[
    ExtBot[None], Context, dict[Any, Any], dict[Any, Any], dict[Any, Any], None
]


builder = (
    ApplicationBuilder()
    .context_types(ContextTypes(context=Context))
    .job_queue(None)
    .token(settings.TGBOT_TOKEN.get_secret_value())
)


tg_app = (
    builder.updater(None).build() if settings.TGBOT_WEBHOOK_URL else builder.build()
)
