from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class UserTGData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tg_id: Annotated[int, Field(alias="id")]
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""
    is_bot: bool = False
