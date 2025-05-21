from pathlib import Path

import structlog
from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from app.auth.errors import InvalidInviteCodeError
from app.auth.services import TGInviteCodesService, TGUserService
from app.conf import settings
from app.core.errors import AppError
from app.core.llm import load_prompts
from app.tgbot.context import Context
from app.tgbot.decorators import db_session, requires_auth
from app.tgbot.utils import (
    LocalizedTexts,
    extract_user_data,
    get_invite_code,
    get_texts,
)

logger = structlog.get_logger()


class StartTexts(BaseModel):
    welcome_text: str
    welcome_back_text: str


class HandlersTexts(BaseModel):
    start: StartTexts


class Texts(LocalizedTexts[HandlersTexts]):
    en: HandlersTexts
    ru: HandlersTexts


try:
    TEXTS = load_prompts(
        Path(__file__).parent / "texts.yaml",
        Texts,
        key="handlers",
    )
except:
    logger.error("Failed to load PostGenerator prompts")
    raise


@db_session
async def start(update: Update, context: Context) -> None:
    user_data = extract_user_data(update)
    if user_data is None:
        raise AppError("User data is None")
    # TODO: provide in context
    if not context.db_session:
        raise AppError("DB session is None")

    texts = get_texts(TEXTS, user_data.language_code)
    chat = update.effective_chat
    if not chat:
        return

    user_svc = TGUserService(context.db_session)
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


@db_session
@requires_auth(is_admin=True)
async def generate_invites(update: Update, context: Context) -> None:
    logger.info("Generating invites by admin")
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")
    if not context.tg_user:
        raise ValueError("TG user is None")

    if not context.tg_user.is_admin:
        logger.exception(
            "[CRITICAL] User is not admin accessed private endpoint - generate_invites",
            tg_user_id=context.tg_user.tg_id,
        )
        return

    agent_job_svc = TGInviteCodesService(context.db_session)
    invites = await agent_job_svc.create(
        amount=10, uses=1, tg_user_id=context.tg_user.tg_id, is_created_by_admin=True
    )

    chat = update.effective_chat
    if not chat:
        return

    invites_str = "\n".join(
        [
            f'{i + 1}. <a href="https://t.me/{settings.TGBOT_NAME}?start={invite.code}">{invite.code}</a>'
            for i, invite in enumerate(invites)
        ]
    )
    message_text = f"<b>Invites:</b>\n\n{invites_str}"
    await chat.send_message(
        text=message_text,
        parse_mode=ParseMode.HTML,
    )


@db_session
@requires_auth(is_admin=True)
async def generate_invite_1(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


@db_session
@requires_auth(is_admin=True)
async def generate_invite_10(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


@db_session
@requires_auth(is_admin=True)
async def generate_invite_30(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


async def generate_invite(uses: int, update: Update, context: Context) -> None:
    logger.info("Generating invite 1 by admin with {uses} uses")
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")
    if not context.tg_user:
        raise ValueError("TG user is None")

    if not context.tg_user.is_admin:
        logger.exception(
            "[CRITICAL] User is not admin accessed private endpoint - generate_invites",
            tg_user_id=context.tg_user.tg_id,
        )
        return

    agent_job_svc = TGInviteCodesService(context.db_session)
    invites = await agent_job_svc.create(
        amount=1, uses=uses, tg_user_id=context.tg_user.tg_id, is_created_by_admin=True
    )

    chat = update.effective_chat
    if not chat:
        return

    invites_str = "\n".join(
        [
            f'{i + 1}. <a href="https://t.me/{settings.TGBOT_NAME}?start={invite.code}">https://t.me/{settings.TGBOT_NAME}?start={invite.code}</a>'
            for i, invite in enumerate(invites)
        ]
    )
    message_text = f"<b>Invites:</b>\n\n{invites_str}"
    await chat.send_message(
        text=message_text,
        parse_mode=ParseMode.HTML,
    )


UUID_PATTERN = r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}"

handlers = [
    CommandHandler("start", start),
    CommandHandler("generate_invites", generate_invites),
    CommandHandler("generate_invite_1", generate_invite_1),
    CommandHandler("generate_invite_10", generate_invite_10),
    CommandHandler("generate_invite_30", generate_invite_30),
]
