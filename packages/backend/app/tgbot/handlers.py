import structlog
from dishka import FromDishka
from telegram import Chat, Update, WebAppInfo
from telegram.ext import CommandHandler

from app.auth.errors import InvalidInviteCodeError
from app.auth.services import TGUserService
from app.conf import settings
from app.core.errors import AppError
from app.tgbot.admin.handlers import handlers as admin_handlers
from app.tgbot.context import Context
from app.tgbot.dishka import inject
from app.tgbot.i18n import HandlersTexts
from app.tgbot.utils import extract_user_data, get_invite_code, keyboard

logger = structlog.get_logger()


@inject
async def start(
    update: Update,
    context: Context,
    texts: FromDishka[HandlersTexts],
    chat: FromDishka[Chat],
    user_svc: FromDishka[TGUserService],
) -> None:
    user_data = extract_user_data(update)
    if user_data is None:
        raise AppError("User data is None", chat_id=chat.id)

    user = await user_svc.get_user_and_update(user_data)
    if not user:
        invite_code = get_invite_code(context)
        try:
            user = await user_svc.create(user_data, invite_code=invite_code)
        except InvalidInviteCodeError as e:
            logger.exception(e)
            await chat.send_message(
                text=texts.start.welcome_text,
            )
            return
        text = texts.start.welcome_text
    else:
        text = texts.start.welcome_back_text

    await chat.send_message(
        text=text,
        reply_markup=keyboard(
            [(texts.start.button_setup, WebAppInfo(settings.WEBAPP_URL))]
        ),
    )


handlers = [
    CommandHandler("start", start),
    *admin_handlers,
]
