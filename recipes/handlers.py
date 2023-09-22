from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import datetime


BUTTON_HANDLING, EXCLUDE_INGREDIENTS, EXCLUDE_INGREDIENTS_HANDLING, CHOOSE_SUB_LENGTH, FINISH_SUBSCRIBING = range(5)

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


def exclude_ingredients(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["plan_choice"] = query.data

    keyboard = [
        [InlineKeyboardButton("Грибы", callback_data="exclude_mushrooms")],
        [InlineKeyboardButton("Глютен", callback_data="exclude_gluten")],
        [InlineKeyboardButton("Молочная продукция", callback_data="exclude_dairy")],
        [InlineKeyboardButton("Я ем всё", callback_data="exclude_nothing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Отметьте, есть ли у вас непереносимость чего-то из списка:\n"

    ingredients_message = query.message.reply_text(text, reply_markup=reply_markup)
    context.user_data["ingredients_message_id"] = ingredients_message.message_id

    context.user_data["exclude_options"] = {
        "exclude_mushrooms": "Грибы",
        "exclude_gluten": "Глютен",
        "exclude_dairy": "Молочная продукция",
        "exclude_nothing": "Больше ничего",
    }
    context.user_data["exclusion_text"] = f"Вы отметили:\n"
    context.user_data["excluded_choices"] = []

    return EXCLUDE_INGREDIENTS_HANDLING


def exclude_ingredients_handling(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "exclude_nothing":
        return CHOOSE_SUB_LENGTH
    else:
        # TODO: actually write down user's choice to work with later
        context.user_data["excluded_choices"].append(query.data)
        user_choice = context.user_data.get("exclude_options").pop(query.data)
        keyboard = []
        for option in context.user_data.get("exclude_options"):
            button = [InlineKeyboardButton(text=context.user_data.get("exclude_options")[option], callback_data=option)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["exclusion_text"] += f"\n- {user_choice}"
        context.bot.edit_message_text(
            text=f"{context.user_data.get('exclusion_text')}\n\nЧто-то ещё?",
            reply_markup=reply_markup,
            message_id=context.user_data.get("ingredients_message_id"),
            chat_id=query.message.chat_id
        )


def choose_sub_length(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    print(f"Excluded choices: {context.user_data.get('excluded_choices')}")

    keyboard = [
        [InlineKeyboardButton("Неделя", callback_data="week_subscription")],
        [InlineKeyboardButton("Месяц", callback_data="month_subscription")],
        [InlineKeyboardButton("3 месяца", callback_data="3_months_subscription")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text("Выберите срок подписки:", reply_markup=reply_markup)

    return FINISH_SUBSCRIBING


def finish_subscribing(update: Update, context: CallbackContext):
    pass
