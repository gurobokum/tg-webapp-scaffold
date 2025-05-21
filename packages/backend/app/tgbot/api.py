import structlog
from fastapi import APIRouter, HTTPException, Request
from telegram import Update

from app.auth.api import router as auth_router
from app.conf import settings
from app.core.http_errors import HTTPForbiddenError

logger = structlog.get_logger()

router = APIRouter(
    prefix="/tgbot",
    tags=["tgbot"],
)

router.include_router(auth_router)


@router.post("/webhook", responses={403: {"model": HTTPForbiddenError}})
async def post_webhook(request: Request) -> None:
    tg_app = request.state.tg_app
    if not settings.TGBOT_WEBHOOK_SECRET_TOKEN:
        logger.exception(
            "[CRITICAL] Webhook secret token is not set, skipping all updates"
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    if (
        request.headers["x-telegram-bot-api-secret-token"]
        != settings.TGBOT_WEBHOOK_SECRET_TOKEN.get_secret_value()
    ):
        logger.exception("[CRITICAL] Invalid secret token for webhook")
        raise HTTPException(status_code=403, detail="Forbidden")
    update = Update.de_json(data=await request.json(), bot=tg_app.bot)
    await tg_app.update_queue.put(update)
