from typing import cast

from redis.asyncio import Redis as AsyncRedis

from app.auth.services import TGUserService
from app.db import AsyncSessionMaker
from app.tgbot.schemas import UserTGData
from app.tgbot.use_cases import broadcast_all_users
from tests.helpers.bot import CollectingRequest, bot_calls, make_offline_bot


async def create_users(session_maker: AsyncSessionMaker, *tg_ids: int) -> None:
    async with session_maker() as session:
        user_svc = TGUserService(session)
        for tg_id in tg_ids:
            await user_svc.create(
                UserTGData.model_validate({"id": tg_id, "username": f"user{tg_id}"})
            )


async def test_broadcast_sends_to_all_users(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2, 3)
    bot = await make_offline_bot()

    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (3, 0)
    sent = [p for e, p in bot_calls(bot) if e == "sendMessage"]
    assert sorted(p["chat_id"] for p in sent) == [1, 2, 3]
    assert all(p["text"] == "hello" for p in sent)
    assert await redis.get("broadcast:test_event:user:2") is not None


async def test_broadcast_marks_blocked_user(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2, 3)
    bot = await make_offline_bot()
    cast(CollectingRequest, bot.request).forbidden_chat_ids.add(2)

    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (2, 1)
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        blocked = await user_svc.get_user(2)
        ok = await user_svc.get_user(1)
    assert blocked is not None and blocked.is_bot_blocked is True
    assert ok is not None and ok.is_bot_blocked is False
    assert await redis.get("broadcast:test_event:user:2") is None


async def test_broadcast_always_skips_admin_blocked_users(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2)
    async with db_session_maker() as session:
        await TGUserService(session).update_user(1, is_banned=True)

    bot = await make_offline_bot()
    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (1, 0)
    sent = [p for e, p in bot_calls(bot) if e == "sendMessage"]
    assert [p["chat_id"] for p in sent] == [2]


async def test_broadcast_can_skip_bot_blocked_users(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2)
    async with db_session_maker() as session:
        user_svc = TGUserService(session)
        assert await user_svc.mark_bot_blocked(1) is True
        assert await user_svc.mark_bot_blocked(1) is False

    bot = await make_offline_bot()
    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
        exclude_bot_blocked=True,
    )

    assert result == (1, 0)
    sent = [p for e, p in bot_calls(bot) if e == "sendMessage"]
    assert [p["chat_id"] for p in sent] == [2]


async def test_broadcast_unblocks_reachable_bot_blocked_user(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1)
    async with db_session_maker() as session:
        await TGUserService(session).mark_bot_blocked(1)

    bot = await make_offline_bot()
    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (1, 0)
    async with db_session_maker() as session:
        user = await TGUserService(session).get_user(1)
    assert user is not None
    assert user.is_bot_blocked is False


async def test_broadcast_skips_already_sent(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2)
    await redis.set("broadcast:test_event:user:1", "1")
    bot = await make_offline_bot()

    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (1, 0)
    sent = [p for e, p in bot_calls(bot) if e == "sendMessage"]
    assert [p["chat_id"] for p in sent] == [2]


async def test_broadcast_resume_returns_cumulative_counts(
    db_session_maker: AsyncSessionMaker, redis: AsyncRedis
) -> None:
    await create_users(db_session_maker, 1, 2)
    await redis.set("broadcast:test_event:user:1", "1")
    await redis.set("broadcast:test_event:success", "1")
    bot = await make_offline_bot()

    result = await broadcast_all_users(
        bot,
        "test_event",
        message="hello",
        redis=redis,
        session_maker=db_session_maker,
        delay=0,
    )

    assert result == (2, 0)
    assert await redis.ttl("broadcast:test_event:success") > 0
