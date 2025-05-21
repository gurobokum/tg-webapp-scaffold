from pydantic import BaseModel, ConfigDict


class CreateTGInviteCodes(BaseModel):
    amount: int
    uses: int = 1


class TGInviteCode(BaseModel):
    code: str
    uses: int
    created_at: str
    is_created_by_admin: bool = False


class TGUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tg_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""
    is_bot: bool = False
    is_admin: bool = False

    credits_balance: int
