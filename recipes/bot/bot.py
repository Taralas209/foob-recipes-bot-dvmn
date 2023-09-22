from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from recipes.models import Recipes, Category, Ingredients
from recipes.bot.keyboard import START_KEYBOARD, SUBSCRIPTION
from environs import Env
from config.settings import BOT_TOKEN
from django.utils import timezone
import datetime
import logging

INGREDIENTS = []
NUMBER_RECIPE_CHANGES = 2
TODAY = {}


def start(update: Update, _):
    global INGREDIENTS
    global NUMBER_RECIPE_CHANGES

    if NUMBER_RECIPE_CHANGES > 0:
        recipe = Recipes.objects.order_by('?').first()
        title = recipe.title
        image = recipe.image
        description = recipe.description
        category = recipe.category
        update.message.reply_photo(image)
        update.message.reply_text(
            f'<b>{title}\n\n</b>'
            f'{description}\n\n'
            f'<b>Категория:</b> {category}',
            reply_markup=START_KEYBOARD,
            parse_mode='HTML'
        )
        update.message.reply_text(
            'Хотите получать ежедневное меню и не беспокоиться о том, что приготовить завтра? 🍔 🫤\n\n'
            'Оформите нашу подписку, и мы побеспокоимся за вас ⬇️',
            reply_markup=SUBSCRIPTION)
        INGREDIENTS.append(recipe)
    else:
        update.message.reply_text('Вы можете сменить рецепт не более двух раз за сутки!\n\n'
                                  '<b>Хотите использовать наш функционал по максимуму, а также ежедневно получать индивидуальное меню?\n\n</b>'
                                  'Оформите подписку на наш сервис ⬇️',
                                  reply_markup=SUBSCRIPTION,
                                  parse_mode='HTML')


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
        title = recipe.title
        image = recipe.image
        description = recipe.description
        category = recipe.category

        query.message.reply_photo(image)
        query.message.reply_text(
            f'<b>{title}\n\n</b>'
            f'{description}\n\n'
            f'<b>Категория:</b> {category}',
            reply_markup=START_KEYBOARD,
            parse_mode='HTML'
        )
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


def get_subscribe(update: Update, _):
    """Оформить подписку."""
    query = update.callback_query
    query.answer()

    query.message.reply_text(
        'Спасибо, за подписку на наш сервис ❤️\n\n'
        'Выше мы оставили для Вас меню на сегодня ⬆️')
    query.message.reply_text(f'{query.data}')


def main():
    global TODAY
    global NUMBER_RECIPE_CHANGES

    env = Env()
    env.read_env()

    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(get_another_dish, pattern='another_dish'))
    dp.add_handler(CallbackQueryHandler(get_dish_ingredients, pattern='dish_ingredients'))
    # dp.add_handler(CallbackQueryHandler(get_subscribe, pattern='subscribe'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
