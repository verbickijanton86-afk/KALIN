from aiogram import Router, types, F
from aiogram.types import LabeledPrice, PreCheckoutQuery
from config import STAR_PRICE, ADMIN_ID
from database import db

payments_router = Router()


@payments_router.callback_query(F.data.startswith("show_sender_"))
async def show_sender_callback(callback: types.CallbackQuery):
    """Обработка нажатия на кнопку 'Узнать автора'"""
    try:
        message_id = int(callback.data.split("_")[2])
    except:
        await callback.answer("❌ Ошибка в данных", show_alert=True)
        return

    # Проверяем, платил ли уже пользователь
    payments = await db.get_user_payments(callback.from_user.id, message_id)

    if payments:
        # Уже платил - показываем информацию
        sender_id = await db.get_message_sender(message_id)
        await callback.answer(
            f"👤 Автор сообщения: ID {sender_id}",
            show_alert=True
        )
        return

    # Ещё не платил - предлагаем оплату
    prices = [LabeledPrice(label="Узнать автора", amount=STAR_PRICE)]

    try:
        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            title="Узнать автора сообщения",
            description=f"Сообщение #{message_id}",
            payload=f"message_{message_id}",
            currency="XTR",  # Telegram Stars
            prices=prices
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(
            f"❌ Ошибка платежа: {str(e)}",
            show_alert=True
        )
        print(f"PAYMENT ERROR: {e}")


@payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Обработка до совершения платежа"""
    await pre_checkout_query.answer(ok=True)


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    """Обработка успешного платежа"""
    try:
        payload = message.successful_payment.invoice_payload

        if not payload.startswith("message_"):
            await message.answer("❌ Неверный платёж")
            return

        message_id = int(payload.split("_")[1])
        amount = message.successful_payment.total_amount

        # Сохраняем платёж в БД
        await db.save_payment(message.from_user.id, message_id, amount)

        # Получаем ID автора
        sender_id = await db.get_message_sender(message_id)

        if not sender_id:
            await message.answer("❌ Сообщение не найдено")
            return

        # Отправляем информацию пользователю
        await message.answer(
            f"✅ Спасибо за платёж!\n\n"
            f"👤 <b>Автор сообщения:</b> <code>{sender_id}</code>\n\n"
            f"(ID скопирован)",
            parse_mode="HTML"
        )

        # Уведомляем админа о покупке
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 Пользователь {message.from_user.id} платил {amount} звёзд за сообщение #{message_id}"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке платежа: {str(e)}")
        print(f"PAYMENT PROCESSING ERROR: {e}")
