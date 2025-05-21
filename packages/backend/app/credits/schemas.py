from pydantic import BaseModel


class BuyCreditsRequest(BaseModel):
    package_name: str


class CreditsPackage(BaseModel):
    package_name: str
    credits_amount: int
    stars_amount: int
