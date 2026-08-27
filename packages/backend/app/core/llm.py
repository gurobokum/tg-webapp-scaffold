from functools import lru_cache
from typing import Literal, TypeAlias, TypeVar

import structlog
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, TypeAdapter
from ruamel.yaml import YAML

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


PromptType = TypeVar("PromptType", bound=BaseModel)


@lru_cache
def load_prompts(
    path: str, model_type: type[PromptType], *, key: str | None = None
) -> PromptType:
    type_adapter = TypeAdapter(model_type)
    with open(path) as fd:
        data = YAML().load(fd)
        return type_adapter.validate_python(data[key] if key else data)
