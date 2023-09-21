from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import datetime


BUTTON_HANDLING, EXCLUDE_INGREDIENTS = range(2)

# Subscribed user's menu


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
    if update.message:
        menu_message = update.message.reply_text(text, reply_markup=reply_markup)
    else:
        menu_message = update.callback_query.message.reply_text(text, reply_markup=reply_markup)

    context.user_data["menu_message_id"] = menu_message.message_id

    return BUTTON_HANDLING


def button_handling(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    today = datetime.date.today()
    if query.data == "yesterday":
        context.user_data["plan_date"] = today - datetime.timedelta(days=1)
        return show_daily_plan(update, context)
    elif query.data == "today":
        context.user_data["plan_date"] = today
        return show_daily_plan(update, context)
    elif query.data == "tomorrow":
        context.user_data["plan_date"] = today + datetime.timedelta(days=1)
        return show_daily_plan(update, context)
    elif query.data == "back":
        return show_user_menu(update, context)


def show_daily_plan(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    menu_message_id = context.user_data.get("menu_message_id")
    date = context.user_data.get("plan_date")
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(
        text=f"Вот ваш план на {date}\n\n- Рецепт 1\n- Рецепт 2\n...",
        reply_markup=reply_markup,
        message_id=menu_message_id,
        chat_id=query.message.chat_id,
    )

# Process of subscription


def start_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Классический", callback_data="classic_plan")],
        [InlineKeyboardButton("Вегетарианский", callback_data="vegetarian_plan")],
        [InlineKeyboardButton("Низкоуглеводный", callback_data="low_carb_plan")],
        [InlineKeyboardButton("Спортивный", callback_data="sport_plan")],
        [InlineKeyboardButton("Кето", callback_data="keto_plan")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Отлично! Для начала выберите на какой план вы хотите подписаться:"

    query.message.reply_text(text, reply_markup=reply_markup)

    return EXCLUDE_INGREDIENTS

