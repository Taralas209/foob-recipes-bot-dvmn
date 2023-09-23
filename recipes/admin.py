from django.contrib import admin
from .models import Recipes, Category, Ingredients,User, SubscriptionPlan
import json

admin.site.register(Recipes)
admin.site.register(Category)
admin.site.register(Ingredients)
admin.site.register(User)


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'readable_daily_plans')

    def readable_daily_plans(self, obj):
        try:
            daily_plans_dict = json.loads(obj.daily_plans)
            readable_str = ""
            for date, recipes in daily_plans_dict.items():
                readable_str += f"{date}:\n"
                for recipe in recipes:
                    readable_str += f"  - {recipe}\n"
            return readable_str
        except json.JSONDecodeError:
            return "Error: Invalid JSON Data"

    readable_daily_plans.short_description = 'Планы на каждый день'


admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
