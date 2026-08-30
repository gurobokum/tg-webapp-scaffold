from typing import Annotated

from pydantic import BaseModel, Field


class UserTGData(BaseModel):
    tg_id: Annotated[int, Field(alias="id")]
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""
    is_bot: bool = False
