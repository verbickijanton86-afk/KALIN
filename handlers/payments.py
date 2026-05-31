from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
import database as db
import config

payments_router = Router()


@payments_router.callback_query(F.data.startswith("pay_"))
async def create_stars_invoice(callback: CallbackQuery, bot: Bot):
    # Только админ может запрашивать деанон
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("❌ У вас нет доступа к этой функции.", show_alert=True)
        return

    admin_msg_id = int(callback.data.split("_")[1])

    # Формируем счет на 10 Telegram Stars
    prices = [LabeledPrice(label="XTR", amount=10)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Раскрытие автора",
        description=f"Плата за просмотр данных автора сообщения #{admin_msg_id}",
        prices=prices,
        provider_token="",  # Для Telegram Stars оставляем пустым!
        currency="XTR",
        payload=f"deanon_{admin_msg_id}",  # Передаем ID сообщения внутри payload
        start_parameter="deanon"
    )
    await callback.answer()


@payments_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Автоматически одобряем платеж
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload
    admin_msg_id = int(payload.split("_")[1])

    # Получаем автора из БД
    author_data = await db.get_author(admin_msg_id)

    if author_data:
        user_id, username, full_name = author_data
        result_text = (
            "✅ **Оплата прошла успешно!**\n\n"
            f"👤 **Данные автора:**\n"
            f"🔹 Имя: {full_name}\n"
            f"🔹 Юзернейм: @{username}\n"
            f"🔹 ID: `{user_id}`"
        )
    else:
        result_text = "⚠️ Оплата принята, но данные автора не найдены в текущей сессии базы данных."

    await message.answer(result_text, parse_mode="Markdown")
