from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from recipes.models import Recipes, Category, Ingredients
import os
import django


def start(update: Update, context: CallbackContext):
    recipe = Recipes.objects.order_by('?').first()
    title = recipe.title
    image = recipe.image
    description = recipe.description
    category = recipe.category
    update.message.reply_text(title)


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()

    updater = Updater(token='6007886215:AAG1S68on3MjZnJ5bSB2fLrwgfMNVPKZFtI')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start, run_async=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
