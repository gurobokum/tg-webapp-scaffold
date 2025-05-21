from fastapi import APIRouter, status

from app.auth.schemas import TGUser as TGUserSchema
from app.dependencies import AuthUser
from app.openapi import generate_unique_id_function

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    generate_unique_id_function=generate_unique_id_function("auth"),
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def me(
    user: AuthUser,
) -> TGUserSchema:
    return TGUserSchema.model_validate(user)
