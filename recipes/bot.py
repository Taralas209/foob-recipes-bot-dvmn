import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from recipes.models import Recipes, Category, Ingredients
from keyboard import START_KEYBOARD, SUBSCRIPTION
from environs import Env
from config.settings import BOT_TOKEN


def get_random_recipe():
    """Случайный рецепт."""
    recipe = Recipes.objects.order_by('?').first()
    # title = recipe.title
    # image = recipe.image
    # description = recipe.description
    # category = recipe.category
    # return {
    #     'title':title,
    #    'image': image,
    #     'description':description,
    #     'category':category
    # }
    return recipe


def start(update: Update, _):
    recipe = get_random_recipe()
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


def restart(update, context):
    update.message.reply_text("Бот перезапущен!")
    context.user_data.clear()
    return start(update, context)


def get_another_dish(update: Update, context: CallbackContext):
    """Выбрать другой рецепт."""
    query = update.callback_query
    query.answer()

    recipe = get_random_recipe()
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


def get_dish_ingredients(update: Update, _):
    """Показать Ингредиенты блюда."""
    recipe = get_random_recipe()
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{recipe.ingredients.all()}',reply_markup=START_KEYBOARD)


def get_subscribe(update: Update, _):
    """Оформить подписку."""
    query = update.callback_query
    query.answer()

    query.message.reply_text(
        'Спасибо, за подписку на наш сервис ❤️\n\n'
        'Выше мы оставили для Вас меню на сегодня ⬆️')
    query.message.reply_text(f'{query.data}')


def main():
    env = Env()
    env.read_env()

    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(get_another_dish, pattern='another_dish'))
    dp.add_handler(CallbackQueryHandler(get_dish_ingredients, pattern='dish_ingredients'))
    #dp.add_handler(CallbackQueryHandler(get_subscribe, pattern='subscribe'))
    dp.add_handler(CommandHandler('restart', restart))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
