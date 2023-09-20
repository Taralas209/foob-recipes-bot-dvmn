from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


BUTTON_HANDLING = range(1)


def show_user_menu(update: Update, context: CallbackContext):
    menu = context.user_data.get("menu_selection")
    expiration_date = context.user_data.get("expiration_date")

    text = f"У вас подписка на {menu} до {expiration_date}:\n\nВыберите кнопку, чтобы посмотреть рацион на:"
    keyboard = [
        [
            InlineKeyboardButton(text="Вчера", callback_data="yesterday"),
            InlineKeyboardButton(text="Сегодня", callback_data="today"),
            InlineKeyboardButton(text="Завтра", callback_data="tomorrow")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)

    return BUTTON_HANDLING

