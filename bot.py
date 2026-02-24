import os
from telegram import (
    Update,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = -1003754999422

user_data = {}

# ---------- старт ----------
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"step": "brand", "photos": []}
    update.message.reply_text("🚗 Напиши марку и модель авто")

# ---------- кнопка «Новое объявление» ----------
def restart_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    user_data[chat_id] = {"step": "brand", "photos": []}

    query.message.reply_text("🚗 Напиши марку и модель авто")

# ---------- текст ----------
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        update.message.reply_text("Нажми /start")
        return

    step = user_data[chat_id]["step"]

    if step == "brand":
        user_data[chat_id]["brand"] = text
        user_data[chat_id]["step"] = "year"
        update.message.reply_text("📅 Год выпуска?")

    elif step == "year":
        user_data[chat_id]["year"] = text
        user_data[chat_id]["step"] = "price"
        update.message.reply_text("💰 Цена?")

    elif step == "price":
        user_data[chat_id]["price"] = text
        user_data[chat_id]["step"] = "mileage"
        update.message.reply_text("📏 Пробег?")

    elif step == "mileage":
        user_data[chat_id]["mileage"] = text
        user_data[chat_id]["step"] = "description"
        update.message.reply_text("🧾 Краткое описание авто")

    elif step == "description":
        user_data[chat_id]["description"] = text
        user_data[chat_id]["step"] = "photos"
        update.message.reply_text("📸 Загрузи фото.\nКогда закончишь — напиши ГОТОВО")

    elif step == "photos":
        if text.lower() == "готово":
            if not user_data[chat_id]["photos"]:
                update.message.reply_text("❗ Добавь хотя бы одно фото")
                return

            d = user_data[chat_id]

            caption = (
                f"🚗 {d['brand']}\n\n"
                f"📅 Год: {d['year']}\n"
                f"💰 Цена: {d['price']}\n"
                f"📏 Пробег: {d['mileage']}\n\n"
                f"🧾 {d['description']}\n\n"
                f"📲 Пишите в ЛС"
            )

            media = []
            for i, photo_id in enumerate(d["photos"]):
                if i == 0:
                    media.append(InputMediaPhoto(photo_id, caption=caption))
                else:
                    media.append(InputMediaPhoto(photo_id))

            context.bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=media
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Новое объявление", callback_data="restart")]
            ])

            update.message.reply_text(
                "✅ Объявление опубликовано в канале",
                reply_markup=keyboard
            )

            user_data.pop(chat_id)

        else:
            update.message.reply_text("📸 Загрузи фото или напиши ГОТОВО")

# ---------- фото ----------
def handle_photo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if chat_id in user_data and user_data[chat_id]["step"] == "photos":
        photo_id = update.message.photo[-1].file_id
        user_data[chat_id]["photos"].append(photo_id)
        update.message.reply_text("📸 Фото добавлено")

# ---------- main ----------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(restart_callback, pattern="restart"))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Бот запущен")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()