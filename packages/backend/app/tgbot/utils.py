from typing import Generic, TypeVar, cast

from pydantic import BaseModel
from telegram import Update

from app.tgbot.context import Context
from app.tgbot.schemas import UserTGData


def extract_user_data(update: Update) -> UserTGData | None:
    try:
        user = next(
            getattr(update, attr)
            for attr in [
                "message",
                "edited_message",
                "inline_query",
                "chosen_inline_result",
                "callback_query",
                "poll",
                "poll_answer",
                "pre_checkout_query",
            ]
            if hasattr(update, attr) and getattr(update, attr) is not None
        ).from_user
    except StopIteration:
        return None

    return UserTGData.model_validate_json(user.to_json())


T = TypeVar("T", bound=BaseModel)


class LocalizedTexts(BaseModel, Generic[T]):
    en: T
    ru: T


def get_texts(texts: LocalizedTexts[T], lang: str) -> T:
    if lang not in ("en", "ru"):
        lang = "ru"

    bundle = getattr(texts, lang)
    if not bundle:
        raise ValueError(f"Language {lang} not found in bundle")
    return cast(T, bundle)


def get_invite_code(context: Context) -> str | None:
    if not context or not context.args:
        return None

    payload = context.args[0]
    return str(payload).split("&")[0].strip()
