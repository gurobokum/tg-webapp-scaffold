from functools import lru_cache
from typing import TypeVar

from pydantic import BaseModel, TypeAdapter
from ruamel.yaml import YAML

YamlType = TypeVar("YamlType", bound=BaseModel)


@lru_cache
def load_yaml(
    path: str, model_type: type[YamlType], *, key: str | None = None
) -> YamlType:
    type_adapter = TypeAdapter(model_type)
    with open(path) as fd:
        data = YAML().load(fd)
        return type_adapter.validate_python(data[key] if key else data)
