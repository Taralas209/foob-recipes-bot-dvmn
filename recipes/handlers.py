from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from .models import SubscriptionPlan, User, Recipes, Category
import datetime
import random


BUTTON_HANDLING, EXCLUDE_INGREDIENTS, EXCLUDE_INGREDIENTS_HANDLING, CHOOSE_SUB_LENGTH, FINISH_SUBSCRIBING = range(5)


PLAN_OPTIONS = {
        "classic_plan": "Классический",
        "vegetarian_plan": "Вегетарианский",
        "low_carb_plan": "Низкоуглеводный",
        "sport_plan": "Спортивный",
        "keto_plan": "Кето",
    }

# Subscribed user's menu


def show_user_menu(update: Update, context: CallbackContext):
    menu = context.user_data.get("plan_choice")
    expiration_date = context.user_data.get("sub_end_date")

    text = f"У вас подписка на план \"{PLAN_OPTIONS[menu]}\" до {expiration_date}:\n\nВыберите кнопку, чтобы посмотреть рацион на:"
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

    # keyboard = [
    #     [InlineKeyboardButton("Классический", callback_data="classic_plan")],
    #     [InlineKeyboardButton("Вегетарианский", callback_data="vegetarian_plan")],
    #     [InlineKeyboardButton("Низкоуглеводный", callback_data="low_carb_plan")],
    #     [InlineKeyboardButton("Спортивный", callback_data="sport_plan")],
    #     [InlineKeyboardButton("Кето", callback_data="keto_plan")],
    # ]
    keyboard = []
    for option in PLAN_OPTIONS:
        button = [InlineKeyboardButton(text=PLAN_OPTIONS[option], callback_data=option)]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Отлично! Для начала выберите на какой план вы хотите подписаться:"

    query.message.reply_text(text, reply_markup=reply_markup)

    return CHOOSE_SUB_LENGTH

    # return EXCLUDE_INGREDIENTS
#
#
# def exclude_ingredients(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#     context.user_data["plan_choice"] = query.data
#
#     keyboard = [
#         [InlineKeyboardButton("Грибы", callback_data="exclude_mushrooms")],
#         [InlineKeyboardButton("Глютен", callback_data="exclude_gluten")],
#         [InlineKeyboardButton("Молочная продукция", callback_data="exclude_dairy")],
#         [InlineKeyboardButton("Я ем всё", callback_data="exclude_nothing")]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     text = "Отметьте, есть ли у вас непереносимость чего-то из списка:\n"
#
#     ingredients_message = query.message.reply_text(text, reply_markup=reply_markup)
#     context.user_data["ingredients_message_id"] = ingredients_message.message_id
#
#     context.user_data["exclude_options"] = {
#         "exclude_mushrooms": "Грибы",
#         "exclude_gluten": "Глютен",
#         "exclude_dairy": "Молочная продукция",
#         "exclude_nothing": "Больше ничего",
#     }
#     context.user_data["exclusion_text"] = f"Вы отметили:\n"
#     context.user_data["excluded_choices"] = []
#
#     return EXCLUDE_INGREDIENTS_HANDLING


# def exclude_ingredients_handling(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#
#     if query.data == "exclude_nothing":
#         return CHOOSE_SUB_LENGTH
#     else:
#         # TODO: actually write down user's choice to work with later
#         user_choice = context.user_data.get("exclude_options").pop(query.data)
#         context.user_data["excluded_choices"].append(user_choice)
#         keyboard = []
#         for option in context.user_data.get("exclude_options"):
#             button = [InlineKeyboardButton(text=context.user_data.get("exclude_options")[option], callback_data=option)]
#             keyboard.append(button)
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         context.user_data["exclusion_text"] += f"\n- {user_choice}"
#         context.bot.edit_message_text(
#             text=f"{context.user_data.get('exclusion_text')}\n\nЧто-то ещё?",
#             reply_markup=reply_markup,
#             message_id=context.user_data.get("ingredients_message_id"),
#             chat_id=query.message.chat_id
#         )


def choose_sub_length(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data["plan_choice"] = query.data

    keyboard = [
        [InlineKeyboardButton("3 дня", callback_data="3_day_subscription")],
        [InlineKeyboardButton("5 дней", callback_data="5_day_subscription")],
        [InlineKeyboardButton("7 дней", callback_data="7_day_subscription")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text("Выберите срок подписки:", reply_markup=reply_markup)

    return FINISH_SUBSCRIBING


def finish_subscribing(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    today = datetime.date.today()
    if query.data == "3_day_subscription":
        end_date = today + datetime.timedelta(days=3)
    elif query.data == "5_day_subscription":
        end_date = today + datetime.timedelta(days=5)
    elif query.data == "7_day_subscription":
        end_date = today + datetime.timedelta(days=7)

    context.user_data["sub_end_date"] = end_date
    plan_choice = context.user_data["plan_choice"]

    telegram_user_id = query.from_user.id
    user, created = User.objects.get_or_create(
        telegram_id=telegram_user_id,
        defaults={'start_subscription': today, 'end_subscription': end_date, 'is_subscription': True}
    )
    if created:
        user.username = query.from_user.username
        user.save()

    category_title = PLAN_OPTIONS[plan_choice]
    subscription_plan = SubscriptionPlan(user=user, start_date=today, end_date=end_date)
    create_daily_plans(subscription_plan, category_title)
    subscription_plan.save()

    text = f"""Вы успешно подписались на план \"{PLAN_OPTIONS[plan_choice]}\" до {end_date}. \
Воспользуйтесь командой /menu, чтобы посмотреть ваши рецепты!"""

    query.message.reply_text(text=text)

    return ConversationHandler.END


def create_daily_plans(subscription_plan, category_title):
    start_date = subscription_plan.start_date
    end_date = subscription_plan.end_date
    subscription_length = (end_date - start_date).days + 1

    category = Category.objects.get(title=category_title)
    recipes = Recipes.objects.filter(category=category)

    daily_plans_dict = {}
    for day_offset in range(subscription_length):
        day = start_date + datetime.timedelta(days=day_offset)
        daily_recipes = random.sample(list(recipes), min(3, len(recipes)))
        daily_plans_dict[day.isoformat()] = [recipe.title for recipe in daily_recipes]

    subscription_plan.set_daily_plans(daily_plans_dict)
