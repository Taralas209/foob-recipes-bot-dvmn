from django.contrib import admin
from .models import Recipes, Category, Ingredients

admin.site.register(Recipes)
admin.site.register(Category)
admin.site.register(Ingredients)
