from typing import Literal, TypeAlias

import structlog
from langchain_openai import ChatOpenAI

from app.conf import settings

logger = structlog.get_logger()

LLMModel: TypeAlias = ChatOpenAI

LLMModelName = Literal["gpt-4o", "o4-mini", "o3"]


def get_llm(model: LLMModelName = "gpt-4o") -> LLMModel:
    match model:
        case "gpt-4o":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-4o",
            )
        case "o4-mini":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="o4-mini",
            )
        case "o3":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="o3",
            )
        case _:
            raise ValueError(f"Unsupported model: {model}")
