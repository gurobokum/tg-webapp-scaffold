from collections.abc import Sequence
from typing import Generic, TypeVar, cast

from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo

from app.tgbot.context import Context
from app.tgbot.schemas import UserTGData

type KeyboardButton = tuple[str, str | WebAppInfo]


def keyboard(*args: Sequence[KeyboardButton | None]) -> InlineKeyboardMarkup:
    """
    Build an InlineKeyboardMarkup from rows of (label, target) tuples.

    A str target becomes callback_data, a WebAppInfo target becomes a web app
    button. None entries and empty rows are skipped, so call sites can pass
    conditional buttons inline.
    """
    keyboard_markup = []

    for arg in args:
        row = []
        for button in arg:
            if not button:
                continue
            if isinstance(button[1], WebAppInfo):
                row.append(InlineKeyboardButton(button[0], web_app=button[1]))
            else:
                row.append(InlineKeyboardButton(button[0], callback_data=button[1]))

        if not row:
            continue
        keyboard_markup.append(row)

    return InlineKeyboardMarkup(keyboard_markup)


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
