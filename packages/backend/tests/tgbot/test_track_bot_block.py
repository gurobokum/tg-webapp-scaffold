from app.auth.services import TGUserService
from app.db import AsyncSessionMaker
from app.tgbot.handlers import track_bot_block
from app.tgbot.schemas import UserTGData
from tests.helpers.bot import make_offline_bot
from tests.helpers.updates import make_chat_member_update, make_context


async def test_marks_bot_blocked_on_kicked(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        await TGUserService(session).create(UserTGData.model_validate({"id": 5005}))

    bot = await make_offline_bot()
    update = make_chat_member_update(bot, user_id=5005, new_status="kicked")
    context = make_context(bot, db_session_maker)

    await track_bot_block(update, context)

    async with db_session_maker() as session:
        user = await TGUserService(session).get_user(5005)
    assert user is not None
    assert user.is_bot_blocked is True


async def test_marks_bot_unblocked_on_member(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        await user_svc.create(UserTGData.model_validate({"id": 6006}))
        await user_svc.mark_bot_blocked(6006)

    bot = await make_offline_bot()
    update = make_chat_member_update(bot, user_id=6006, new_status="member")
    context = make_context(bot, db_session_maker)

    await track_bot_block(update, context)

    async with db_session_maker() as session:
        user = await TGUserService(session).get_user(6006)
    assert user is not None
    assert user.is_bot_blocked is False
