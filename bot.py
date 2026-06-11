import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ── НАСТРОЙКИ ──────────────────────────────────────────────
import os
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@edazagotovki"
CHANNEL_URL = "https://t.me/edazagotovki"
PDF_PATH = "menu_final.pdf"  # положи рядом с bot.py
# ───────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)

WELCOME_TEXT = """👋 Привет! Я Алина — мама двух детей и эксперт по умному питанию, на котором худеют.

Готовлю один раз в неделю — и у меня всегда есть домашняя еда на 3 дня вперёд. Без стресса, без срывов, без голода.

🎁 Хочу подарить тебе моё меню на 3 дня ~1400 ккал — вкусно, просто и бюджетно.

Сначала подпишись на мой канал 👇
{channel}

А затем нажми кнопку ниже 👇""".format(channel=CHANNEL_URL)

AFTER_PDF_TEXT = """🔥 Через 3 дня по этому меню ты почувствуешь разницу.

Хочешь такое меню каждую неделю + поддержку и разбор твоего рациона?

👇 Вступай в закрытый клуб — там я веду участниц лично."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Я подписалась 🍽", callback_data="subscribed")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "subscribed":
        # Проверяем подписку
        try:
            member = await context.bot.get_chat_member(CHANNEL, query.from_user.id)
            is_subscribed = member.status in ["member", "administrator", "creator"]
        except Exception:
            is_subscribed = False

        if not is_subscribed:
            keyboard = [[InlineKeyboardButton("Я подписалась 🍽", callback_data="subscribed")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"❗️ Кажется, ты ещё не подписалась на канал.\n\n"
                f"Подпишись здесь: {CHANNEL_URL}\n\n"
                f"И нажми кнопку снова 👇",
                reply_markup=reply_markup
            )
            return

        # Отправляем PDF
        await query.message.reply_text("Отлично, держи! 🎉 Сейчас пришлю меню...")

        try:
            with open(PDF_PATH, "rb") as pdf:
                await context.bot.send_document(
                    chat_id=query.from_user.id,
                    document=pdf,
                    filename="Меню на 3 дня.pdf",
                    caption="🥗 Меню на 3 дня · ~1400 ккал\nГотовишь один раз — ешь три дня!"
                )
        except FileNotFoundError:
            await query.message.reply_text(
                "⚠️ PDF временно недоступен. Напиши мне напрямую — пришлю вручную."
            )
            return

        # Через 2 секунды — оффер
        await asyncio.sleep(2)
        keyboard = [[InlineKeyboardButton("Хочу в клуб →", url=CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=AFTER_PDF_TEXT,
            reply_markup=reply_markup
        )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
