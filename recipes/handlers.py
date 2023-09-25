from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from .models import SubscriptionPlan, User, Recipes, Category
import datetime
import random


BUTTON_HANDLING, EXCLUDE_INGREDIENTS, EXCLUDE_INGREDIENTS_HANDLING, CHOOSE_SUB_LENGTH, FINISH_SUBSCRIBING = range(5)


PLAN_OPTIONS = {
        "classic_plan": "Стандартный",
        "vegetarian_plan": "Вегетарианский",
        "low_carb_plan": "Низкоуглеводный",
        "sport_plan": "Спортивный",
        "keto_plan": "Кето",
    }


# Process of subscription
def start_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    telegram_user_id = query.from_user.id
    user, created = User.objects.get_or_create(
        telegram_id=telegram_user_id
    )

    active_subscription = user.current_subscription_plan
    if active_subscription and active_subscription.end_date >= datetime.date.today():
        plan_choice = PLAN_OPTIONS.get(active_subscription.plan_choice, "Неизвестный план")
        query.message.reply_text(text=f"У вас уже есть активная подписка на план \"{plan_choice}\" до {active_subscription.end_date}.")
        return show_user_menu(update, context)

    keyboard = []
    for option in PLAN_OPTIONS:
        button = [InlineKeyboardButton(text=PLAN_OPTIONS[option], callback_data=option)]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Отлично! Для начала выберите на какой план вы хотите подписаться:"

    query.message.reply_text(text, reply_markup=reply_markup)

    return CHOOSE_SUB_LENGTH



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
        end_date = today + datetime.timedelta(days=2)
    elif query.data == "5_day_subscription":
        end_date = today + datetime.timedelta(days=4)
    elif query.data == "7_day_subscription":
        end_date = today + datetime.timedelta(days=6)

    context.user_data["sub_end_date"] = end_date
    plan_choice = context.user_data["plan_choice"]

    telegram_user_id = query.from_user.id
    user, created = User.objects.get_or_create(
        telegram_id=telegram_user_id
    )

    category_title = PLAN_OPTIONS[plan_choice]

    subscription_plan = SubscriptionPlan(user=user, start_date=today, end_date=end_date, plan_choice=plan_choice)
    create_daily_plans(subscription_plan, category_title)
    subscription_plan.save()

    user.current_subscription_plan = subscription_plan
    user.save()

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


# Subscribed user's menu
def show_user_menu(update: Update, context: CallbackContext):
    menu = context.user_data.get("plan_choice")
    expiration_date = context.user_data.get("sub_end_date")

    telegram_user_id = update.effective_user.id
    user = User.objects.get(telegram_id=telegram_user_id)
    subscription_plan = user.subscription_plans.last()

    if not menu and subscription_plan:
        menu = subscription_plan.plan_choice

    if not expiration_date and subscription_plan:
        expiration_date = subscription_plan.end_date

    if menu not in PLAN_OPTIONS:
        text = "Произошла ошибка: план питания не найден. Пожалуйста, попробуйте еще раз."
    else:
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
        print("Sent menu_message_id: ", menu_message.message_id)
        print("Sent chat_id: ", update.message.chat_id)
    else:
        menu_message = update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        print("Sent menu_message_id: ", menu_message.message_id)
        print("Sent chat_id: ", update.callback_query.message.chat_id)


    context.user_data["menu_message_id"] = menu_message.message_id

    return BUTTON_HANDLING


def button_handling(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    print("button_handling called")
    print("query.data:", query.data)

    if query.data == "back":
        return show_user_menu(update, context)

    user_id = query.from_user.id
    user = User.objects.get(telegram_id=user_id)
    subscription_plan = user.subscription_plans.last()

    today = datetime.date.today()

    if query.data == "yesterday":
        date = today - datetime.timedelta(days=1)
    elif query.data == "today":
        date = today
    elif query.data == "tomorrow":
        date = today + datetime.timedelta(days=1)
    else:
        date = today

    if subscription_plan.start_date <= date <= subscription_plan.end_date:
        context.user_data["plan_date"] = date
        return show_daily_plan(update, context)
    elif date < subscription_plan.start_date:
        query.message.reply_text(f"Ваш план подписки начинается с {subscription_plan.start_date}.")
    else:
        query.message.reply_text(
            f"Ваш план подписки закончился {subscription_plan.end_date}. Пожалуйста, оформите новую подписку.")


def show_daily_plan(update: Update, context: CallbackContext):
    print("show_daily_plan called")
    query = update.callback_query
    query.answer()

    menu_message_id = context.user_data.get("menu_message_id")
    chat_id = query.message.chat_id
    print("menu_message_id: ", menu_message_id)
    print("chat_id: ", chat_id)

    user_id = query.from_user.id
    user = User.objects.get(telegram_id=user_id)
    subscription_plan = user.subscription_plans.last()

    daily_plans = subscription_plan.get_daily_plans()
    date = context.user_data.get("plan_date")
    meals = daily_plans.get(str(date), [])
    print("meals: ", meals)

    # Отправляем каждое блюдо отдельным сообщением
    for meal in meals:
        recipe = Recipes.objects.get(title=meal)
        title = recipe.title
        image = recipe.image
        categories = ", ".join([cat.title for cat in recipe.category.all()]) if recipe.category.all() else "None"

        # Получаем ингредиенты для блюда
        ingredients = recipe.ingredients.all()
        ingredients_list = "\n".join([f"- {ingredient.title}" for ingredient in ingredients])

        # Отправляем фотографию и название блюда, категорию и ингредиенты
        context.bot.send_photo(chat_id=chat_id, photo=image)
        context.bot.send_message(chat_id=chat_id,
                                 text=f"<b>{title}\n\n</b>"
                                      f"<b>Категория:</b> {categories}\n\n"
                                      f"<b>Ингредиенты:</b>\n{ingredients_list}",
                                 parse_mode='HTML')

    # Отправляем кнопку возвращения к меню после всех блюд
    return_menu_button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Меню", callback_data="back")
            ]
        ]
    )
    context.bot.send_message(chat_id=chat_id, text="Выберите другой день нажав кнопку меню",
                             reply_markup=return_menu_button)


