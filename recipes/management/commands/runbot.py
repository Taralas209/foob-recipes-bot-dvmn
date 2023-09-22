from django.core.management.base import BaseCommand
from recipes.bot.bot import main


class Command(BaseCommand):
    help = 'runbot'

    def handle(self, *args, **options):
        main()
