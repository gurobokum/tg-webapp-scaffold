import json
from typing import Any, cast

from telegram import Update
from telegram.ext import ExtBot
from telegram.request import BaseRequest, RequestData

from app.conf import settings

TEST_BOT_ID = 424242


class CollectingRequest(BaseRequest):
    """
    Offline BaseRequest: records outgoing API calls and returns canned
    Telegram responses instead of hitting the network.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.forbidden_chat_ids: set[int] = set()

    @property
    def read_timeout(self) -> float | None:
        return None

    async def initialize(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: RequestData | None = None,
        read_timeout: Any = BaseRequest.DEFAULT_NONE,
        write_timeout: Any = BaseRequest.DEFAULT_NONE,
        connect_timeout: Any = BaseRequest.DEFAULT_NONE,
        pool_timeout: Any = BaseRequest.DEFAULT_NONE,
    ) -> tuple[int, bytes]:
        endpoint = url.rsplit("/", 1)[-1]
        parameters = request_data.parameters if request_data else {}
        self.calls.append((endpoint, parameters))
        if parameters.get("chat_id") in self.forbidden_chat_ids:
            return 403, json.dumps(
                {
                    "ok": False,
                    "error_code": 403,
                    "description": "Forbidden: bot was blocked by the user",
                }
            ).encode()
        return 200, json.dumps(
            {"ok": True, "result": self._result(endpoint, parameters)}
        ).encode()

    def _result(self, endpoint: str, parameters: dict[str, Any]) -> Any:
        match endpoint:
            case "getMe":
                return {
                    "id": TEST_BOT_ID,
                    "is_bot": True,
                    "first_name": "Test Bot",
                    "username": settings.TGBOT_NAME,
                }
            case "sendMessage":
                return {
                    "message_id": len(self.calls),
                    "date": 1,
                    "chat": {"id": parameters["chat_id"], "type": "private"},
                    "text": parameters.get("text", ""),
                }
            case _:
                return True


async def make_offline_bot() -> ExtBot[None]:
    bot: ExtBot[None] = ExtBot(
        token=settings.TGBOT_TOKEN.get_secret_value(),
        request=CollectingRequest(),
        get_updates_request=CollectingRequest(),
    )
    await bot.initialize()
    return bot


def bot_calls(bot_or_update: ExtBot[None] | Update) -> list[tuple[str, dict[str, Any]]]:
    bot = (
        bot_or_update.get_bot() if isinstance(bot_or_update, Update) else bot_or_update
    )
    return cast(CollectingRequest, bot.request).calls
