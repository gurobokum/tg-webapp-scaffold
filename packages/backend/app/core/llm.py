from functools import lru_cache
from typing import Literal, TypeAlias, TypeVar

import structlog
from langchain_community.llms import Replicate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr, TypeAdapter
from ruamel.yaml import YAML

from app.conf import settings

logger = structlog.get_logger()

LLMModel: TypeAlias = ChatOpenAI
ImageLLMModel: TypeAlias = Replicate

LLMModelName = Literal["gpt-4o", "o4-mini", "o3"]
ImageLLMModelName = Literal["recraft-ai/recraft-v3"]


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


def get_image_llm(model: ImageLLMModelName = "recraft-ai/recraft-v3") -> ImageLLMModel:
    match model:
        case "recraft-ai/recraft-v3":
            _set_replicate_key(settings.REPLICATE_API_KEY)
            return Replicate(model=model, model_kwargs={"size": "1365x1024"})
        case _:
            raise ValueError(f"Unsupported model: {model}")


def _set_replicate_key(replicate_api_key: SecretStr) -> None:
    """
    LangChain bug: https://github.com/langchain-ai/langchain/pull/27859
    setting replicate_api_token doesn't work for replicate client
    """
    import os

    os.environ["REPLICATE_API_TOKEN"] = replicate_api_key.get_secret_value()


PromptType = TypeVar("PromptType", bound=BaseModel)


@lru_cache
def load_prompts(
    path: str, model_type: type[PromptType], *, key: str | None = None
) -> PromptType:
    type_adapter = TypeAdapter(model_type)
    with open(path) as fd:
        data = YAML().load(fd)
        return type_adapter.validate_python(data[key] if key else data)
