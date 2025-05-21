from functools import lru_cache
from typing import TypeVar

import boto3
import botocore.config
from pydantic import BaseModel, TypeAdapter
from ruamel.yaml import YAML
from types_boto3_s3 import S3Client

from app.conf import settings

YamlType = TypeVar("YamlType", bound=BaseModel)


@lru_cache
def load_yaml(
    path: str, model_type: type[YamlType], *, key: str | None = None
) -> YamlType:
    type_adapter = TypeAdapter(model_type)
    with open(path) as fd:
        data = YAML().load(fd)
        return type_adapter.validate_python(data[key] if key else data)


@lru_cache(maxsize=1)
def get_s3_client() -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=str(settings.STORAGE_URL),
        aws_access_key_id=settings.STORAGE_ACCESS_KEY.get_secret_value(),
        aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value(),
        config=botocore.config.Config(signature_version="s3v4"),
    )
