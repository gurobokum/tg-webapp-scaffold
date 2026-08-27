from pathlib import Path

import structlog
from dishka import FromDishka, Provider, Scope, provide
from pydantic import BaseModel
from telegram import Update

from app.core.errors import AppError
from app.core.llm import load_prompts
from app.tgbot.utils import LocalizedTexts, extract_user_data, get_texts

logger = structlog.get_logger()

type Language = str


class StartTexts(BaseModel):
    welcome_text: str
    welcome_back_text: str


class HandlersTexts(BaseModel):
    start: StartTexts


class Texts(LocalizedTexts[HandlersTexts]):
    en: HandlersTexts
    ru: HandlersTexts


try:
    TEXTS: Texts = load_prompts(
        Path(__file__).parent / "texts.yaml", Texts, key="handlers"
    )
except Exception:
    logger.error("Failed to load tgbot i18n texts")
    raise


class TGBotI18NProvider(Provider):
    """
    Requires a root provider that supplies Update.
    """

    @provide(scope=Scope.REQUEST)
    def get_language_code(self, update: FromDishka[Update]) -> Language:
        user_data = extract_user_data(update)
        if user_data is None:
            chat = update.effective_chat
            raise AppError("User data is None", chat_id=chat.id if chat else None)
        return user_data.language_code

    @provide(scope=Scope.REQUEST)
    def get_handlers_texts(self, language_code: FromDishka[Language]) -> HandlersTexts:
        return get_texts(TEXTS, language_code)
