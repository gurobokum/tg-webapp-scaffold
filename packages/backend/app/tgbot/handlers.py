import structlog
from dishka import FromDishka
from telegram import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from app.auth.errors import InvalidInviteCodeError
from app.auth.models import TGAdminUser
from app.auth.services import TGInviteCodesService, TGUserService
from app.conf import settings
from app.core.errors import AppError
from app.tgbot.context import Context
from app.tgbot.dishka import inject
from app.tgbot.i18n import HandlersTexts
from app.tgbot.utils import extract_user_data, get_invite_code

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

    await chat.send_message(
        text=texts.start.welcome_back_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Setup", web_app=WebAppInfo(settings.WEBAPP_URL))]]
        ),
    )


@inject
async def generate_invites(
    update: Update,
    context: Context,
    chat: FromDishka[Chat],
    admin: FromDishka[TGAdminUser],
    invite_svc: FromDishka[TGInviteCodesService],
) -> None:
    await _generate_invites(chat, admin, invite_svc, amount=10, uses=1)


@inject
async def generate_invite_1(
    update: Update,
    context: Context,
    chat: FromDishka[Chat],
    admin: FromDishka[TGAdminUser],
    invite_svc: FromDishka[TGInviteCodesService],
) -> None:
    await _generate_invites(chat, admin, invite_svc, amount=1, uses=1)


@inject
async def generate_invite_10(
    update: Update,
    context: Context,
    chat: FromDishka[Chat],
    admin: FromDishka[TGAdminUser],
    invite_svc: FromDishka[TGInviteCodesService],
) -> None:
    await _generate_invites(chat, admin, invite_svc, amount=1, uses=10)


@inject
async def generate_invite_30(
    update: Update,
    context: Context,
    chat: FromDishka[Chat],
    admin: FromDishka[TGAdminUser],
    invite_svc: FromDishka[TGInviteCodesService],
) -> None:
    await _generate_invites(chat, admin, invite_svc, amount=1, uses=30)


async def _generate_invites(
    chat: Chat,
    admin: TGAdminUser,
    invite_svc: TGInviteCodesService,
    *,
    amount: int,
    uses: int,
) -> None:
    logger.info("generate_invites", tg_user_id=admin.tg_id, amount=amount, uses=uses)
    invites = await invite_svc.create(
        amount=amount, uses=uses, tg_user_id=admin.tg_id, is_created_by_admin=True
    )

    invites_str = "\n".join(
        f'{i + 1}. <a href="https://t.me/{settings.TGBOT_NAME}?start={invite.code}">https://t.me/{settings.TGBOT_NAME}?start={invite.code}</a>'
        for i, invite in enumerate(invites)
    )
    await chat.send_message(
        text=f"<b>Invites:</b>\n\n{invites_str}",
        parse_mode=ParseMode.HTML,
    )


handlers = [
    CommandHandler("start", start),
    CommandHandler("generate_invites", generate_invites),
    CommandHandler("generate_invite_1", generate_invite_1),
    CommandHandler("generate_invite_10", generate_invite_10),
    CommandHandler("generate_invite_30", generate_invite_30),
]
