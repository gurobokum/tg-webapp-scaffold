from app.auth.services import TGUserService
from app.db import AsyncSessionMaker
from app.tgbot.handlers import start
from app.tgbot.i18n import TEXTS
from app.tgbot.schemas import UserTGData
from tests.helpers.bot import bot_calls, make_offline_bot
from tests.helpers.updates import make_context, make_update


async def test_start_creates_user(db_session_maker: AsyncSessionMaker) -> None:
    bot = await make_offline_bot()
    update = make_update(bot, user_id=1001, language_code="en")
    context = make_context(bot, db_session_maker)

    await start(update, context)

    endpoint, params = bot_calls(bot)[-1]
    assert endpoint == "sendMessage"
    assert params["text"] == TEXTS.en.start.welcome_text

    async with db_session_maker() as session:
        user = await TGUserService(session).get_user(1001)
    assert user is not None
    assert user.username == "testuser1001"


async def test_start_existing_user_gets_setup_keyboard(
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as session:
        await TGUserService(session).create(
            UserTGData.model_validate(
                {
                    "id": 2002,
                    "username": "testuser2002",
                    "first_name": "Test",
                    "language_code": "ru",
                }
            )
        )
        await session.commit()

    bot = await make_offline_bot()
    update = make_update(bot, user_id=2002, language_code="ru")
    context = make_context(bot, db_session_maker)

    await start(update, context)

    endpoint, params = bot_calls(bot)[-1]
    assert endpoint == "sendMessage"
    assert params["text"] == TEXTS.ru.start.welcome_back_text
    buttons = params["reply_markup"]["inline_keyboard"]
    assert buttons[0][0]["text"] == TEXTS.ru.start.button_setup
    assert "web_app" in buttons[0][0]
