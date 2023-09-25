from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, InputMediaPhoto, InputMedia, InputFile, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler
from recipes.models import Recipes
from recipes.bot.keyboard import START_KEYBOARD, SUBSCRIPTION
from environs import Env
from config.settings import BOT_TOKEN, MEDIA_ROOT, BASE_DIR
from recipes import handlers
import datetime
import os
from pathlib import Path

INGREDIENTS = []
PREVIOUS_INGREDIENT_NUMBER = 0
NUMBER_RECIPE_CHANGES = 2
TODAY = {}

bot = Bot(token=BOT_TOKEN)


def start(context: CallbackContext):
    global INGREDIENTS
    global NUMBER_RECIPE_CHANGES

    if NUMBER_RECIPE_CHANGES > 0:
        recipe = Recipes.objects.order_by('?').first()
        title = recipe.title
        image = recipe.image
        categories = ", ".join([cat.title for cat in recipe.category.all()]) if recipe.category.all() else "None"
        context.bot.send_photo(chat_id=context.job.context, photo=image)
        context.bot.send_message(
            chat_id=context.job.context,
            text=f'<b>{title}\n\n</b>'
                 f'<b>Категория:</b> {categories}',
            reply_markup=START_KEYBOARD,
            parse_mode='HTML'
        )
        context.bot.send_message(
            chat_id=context.job.context,
            text='Хотите получать ежедневное меню и не беспокоиться о том, что приготовить завтра? 🍔 🫤\n\n'
                 'Оформите нашу подписку, и мы побеспокоимся за вас ⬇️',
            reply_markup=SUBSCRIPTION)

        INGREDIENTS.append(recipe)
    else:
        context.bot.send_message(
            chat_id=context.job.context,
            text='Вы можете сменить рецепт не более двух раз за сутки!\n\n'
                 '<b>Хотите использовать наш функционал по максимуму, а также ежедневно получать индивидуальное меню?\n\n</b>'
                 'Оформите подписку на наш сервис ⬇️',
            reply_markup=SUBSCRIPTION,
            parse_mode='HTML')


def restart(update, context):
    update.message.reply_text("Бот перезапущен!")
    context.user_data.clear()
    return start(update, context)


def get_another_dish(update: Update, _):
    """Выбрать другой рецепт."""
    global INGREDIENTS
    global NUMBER_RECIPE_CHANGES
    global TODAY

    query = update.callback_query
    query.answer()

    if TODAY == {} or datetime.datetime.now().date() > TODAY['today']:
        NUMBER_RECIPE_CHANGES = 2

    if NUMBER_RECIPE_CHANGES > 0:
        TODAY['today'] = datetime.datetime.now().date()
        recipe = Recipes.objects.order_by('?').first()
        #recipe_id = recipe.pk
        title = recipe.title
        image = recipe.image
        categories = ", ".join([cat.title for cat in recipe.category.all()]) if recipe.category.all() else "None"



        query.message.reply_photo(image)
        query.message.reply_text(
            f'<b>{title}\n\n</b>'
            f'<b>Категория:</b> {categories}',
            reply_markup=START_KEYBOARD,
            parse_mode='HTML'
        )

        # img_path = os.path.join(BASE_DIR, MEDIA_ROOT, image)
        # print(img_path)
        #
        # with open(img_path, 'rb') as file:
        #     photo = InputMediaPhoto(file)
        #
        # bot.edit_message_media(
        #     chat_id=query.from_user.id,
        #     message_id=query.message.message_id,
        #     media=photo
        # )
        # query.message.edit_media(
        #     media=InputMediaPhoto(photo
        # )
        query.message.reply_text(
            'Хотите получать ежедневное меню и не беспокоиться о том, что приготовить завтра? 🍔 🫤\n\n'
            'Оформите нашу подписку, и мы побеспокоимся за вас ⬇️',
            reply_markup=SUBSCRIPTION)
        INGREDIENTS.append(recipe)
        NUMBER_RECIPE_CHANGES -= 1
    else:
        query.message.reply_text('Вы можете сменить рецепт не более двух раз за сутки!\n\n'
                                 '<b>Хотите использовать наш функционал по максимуму, а также ежедневно получать индивидуальное меню?\n\n</b>'
                                 'Оформите подписку на наш сервис ⬇️',
                                 reply_markup=SUBSCRIPTION,
                                 parse_mode='HTML')


# def get_previous_dish(update: Update):
#     """Получает предыдущее блюдо."""
#     if PREVIOUS_INGREDIENT_NUMBER == 0:
#         pass
#     else:
#         dish_last_number =

def get_dish_ingredients(update: Update, _):
    """Показать Ингредиенты блюда."""
    recipe = INGREDIENTS[-1]
    ingredients = recipe.ingredients.all()
    ingredients_title = [f'{ingredient.title}\n' for ingredient in ingredients]
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        f'{recipe.title.upper()}\n\n<b>Ингредиенты:</b>\n\n{"".join(ingredients_title)}\nПриятного аппетита 😋',
        reply_markup=START_KEYBOARD,
        parse_mode='HTML')


def start_recipe(update, context):
    context.job_queue.run_repeating(start, interval=datetime.timedelta(seconds=86400), first=1,
                                    context=update.message.chat_id)


def main():
    bot.set_my_commands(
        [
            BotCommand("start", "Запустить бота и получить случайный рецепт"),
            BotCommand("menu", "Показать меню с вашим планом")
        ]
    )
    global TODAY
    global NUMBER_RECIPE_CHANGES

    env = Env()
    env.read_env()

    updater = Updater(token=BOT_TOKEN)

    subscribers_menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', handlers.show_user_menu)],
        states={
            handlers.BUTTON_HANDLING: [CallbackQueryHandler(handlers.button_handling)],
        },
        fallbacks=[CommandHandler('restart', restart)]
    )

    subscription_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.start_subscription, pattern='subscribe')],
        states={
            # handlers.EXCLUDE_INGREDIENTS: [CallbackQueryHandler(handlers.exclude_ingredients)],
            # handlers.EXCLUDE_INGREDIENTS_HANDLING: [CallbackQueryHandler(handlers.exclude_ingredients_handling)],
            handlers.CHOOSE_SUB_LENGTH: [CallbackQueryHandler(handlers.choose_sub_length)],
            handlers.FINISH_SUBSCRIBING: [CallbackQueryHandler(handlers.finish_subscribing)],
        },
        fallbacks=[CommandHandler('restart', restart)]
    )

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_recipe))
    dp.add_handler(CallbackQueryHandler(get_another_dish, pattern='another_dish'))
    dp.add_handler(CallbackQueryHandler(get_dish_ingredients, pattern='dish_ingredients'))
    dp.add_handler(CommandHandler('restart', restart))
    dp.add_handler(subscribers_menu_handler)
    dp.add_handler(subscription_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
