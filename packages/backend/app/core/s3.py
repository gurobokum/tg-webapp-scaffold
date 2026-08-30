import asyncio
import hashlib
import io
from datetime import UTC, datetime
from functools import lru_cache

import boto3
import botocore.config
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from telegram import Bot
from types_boto3_s3 import S3Client

from app.conf import settings

LARGE_FILE_TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=10 * 1024 * 1024,
    multipart_chunksize=10 * 1024 * 1024,
)


@lru_cache(maxsize=1)
def get_s3_client() -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=str(settings.STORAGE_URL),
        aws_access_key_id=settings.STORAGE_ACCESS_KEY.get_secret_value(),
        aws_secret_access_key=settings.STORAGE_SECRET_KEY.get_secret_value(),
        config=botocore.config.Config(signature_version="s3v4"),
    )


async def download_from_s3(s3_client: S3Client, file_path: str) -> bytes:
    def download() -> bytes:
        response = s3_client.get_object(Bucket=settings.STORAGE_BUCKET, Key=file_path)
        return response["Body"].read()

    return await asyncio.to_thread(download)


async def save_to_s3(
    s3_client: S3Client,
    buffer: io.BytesIO,
    file_path: str,
    *,
    config: TransferConfig | None = None,
) -> None:
    def upload() -> None:
        s3_client.upload_fileobj(
            buffer, settings.STORAGE_BUCKET, file_path, Config=config
        )

    await asyncio.to_thread(upload)


async def file_exists_in_s3(s3_client: S3Client, file_path: str) -> bool:
    def exists() -> bool:
        try:
            s3_client.head_object(Bucket=settings.STORAGE_BUCKET, Key=file_path)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
        return True

    return await asyncio.to_thread(exists)


async def upload_tg_file_to_s3(
    bot: Bot, file_id: str, *, prefix: str, suffix: str = "jpg"
) -> tuple[str, bytes, bytes]:
    """
    Download a Telegram file and upload it to S3, hashing the content
    for the storage key. Returns (s3_path, file_bytes, sha256_digest).
    """
    file = await bot.get_file(file_id)
    file_bytes = bytes(await file.download_as_bytearray())

    created_at_str = datetime.now(tz=UTC).strftime("%Y%m%d")
    file_hash = hashlib.sha256(file_bytes)
    s3_path = f"{prefix}/{created_at_str}_{file_hash.hexdigest()[:8]}.{suffix}"

    await save_to_s3(get_s3_client(), io.BytesIO(file_bytes), s3_path)
    return s3_path, file_bytes, file_hash.digest()


def get_full_url(file_path: str) -> str:
    base = str(settings.STORAGE_URL).rstrip("/")
    return f"{base}/{settings.STORAGE_BUCKET}/{file_path.lstrip('/')}"


def get_signed_url(
    s3_client: S3Client, file_path: str, *, expires_in: int = 3600
) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.STORAGE_BUCKET, "Key": file_path},
        ExpiresIn=expires_in,
    )
