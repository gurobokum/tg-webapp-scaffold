import json
from uuid import UUID

from telegram import Update
from telegram.ext import MessageHandler, PreCheckoutQueryHandler, filters

from app.core.errors import AppError, NotFoundError
from app.credits.models import CreditsPurchaseStatus
from app.credits.services import TGUserCreditsService
from app.tgbot.context import Context
from app.tgbot.decorators import db_session, requires_auth


@db_session
@requires_auth
async def pre_checkout(update: Update, context: Context) -> None:
    if not context.db_session:
        raise AppError("No db_session in context")

    if not context.tg_user:
        raise AppError("No tg_user in context")

    query = update.pre_checkout_query
    if not query:
        raise AppError("No pre_checkout_query in update")
    payload = json.loads(query.invoice_payload)

    credits_svc = TGUserCreditsService(context.db_session)
    if payload["code"] != "buy_credits":
        raise AppError(
            "Invalid payload code {payload['code']}", tg_user_id=context.tg_user.tg_id
        )
    purchase = await credits_svc.get_purchase(UUID(payload["id"]))
    if not purchase:
        raise NotFoundError("Purchase not found")

    if purchase.tg_user_id != context.tg_user.tg_id:
        raise AppError("User id mismatch")

    if purchase.status == CreditsPurchaseStatus.COMPLETED:
        await query.answer(
            ok=False,
            error_message="Purchase already completed",
        )

    await credits_svc.confirm_purchase(purchase.id)
    await query.answer(ok=True)


@db_session
@requires_auth
async def complete_payment(update: Update, context: Context) -> None:
    if not context.db_session:
        raise AppError("No db_session in context")

    if not context.tg_user:
        raise AppError("No tg_user in context")

    message = update.message
    if not message:
        raise AppError("No message in update")

    successful_payment = message.successful_payment
    if not successful_payment:
        raise AppError("No successful_payment in message")

    payload = json.loads(successful_payment.invoice_payload)

    if payload["code"] != "buy_credits":
        raise AppError(
            "Invalid payload code {payload['code']}", tg_user_id=context.tg_user.tg_id
        )

    credits_svc = TGUserCreditsService(context.db_session)
    purchase = await credits_svc.get_purchase(UUID(payload["id"]))
    if not purchase or purchase.status != CreditsPurchaseStatus.CONFIRMED:
        await message.reply_text(
            "Purchase failed, please contact with @bot_support",
        )
        raise NotFoundError("[CRITICAL] Purchase not found")

    await credits_svc.complete_purchase(
        purchase.id,
        successful_payment.provider_payment_charge_id,
        successful_payment.telegram_payment_charge_id,
    )


handlers = [
    PreCheckoutQueryHandler(pre_checkout),
    MessageHandler(filters.SUCCESSFUL_PAYMENT, complete_payment),
]
