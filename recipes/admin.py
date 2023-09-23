from django.contrib import admin
from .models import Recipes, Category, Ingredients,User, SubscriptionPlan
import json

admin.site.register(Recipes)
admin.site.register(Category)
admin.site.register(Ingredients)
admin.site.register(User)


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'readable_daily_plans')
    readonly_fields = ('readable_daily_plans_detail',)
    exclude = ('daily_plans',)  # Исключите оригинальное поле из формы

    def readable_daily_plans(self, obj):
        return self.format_daily_plans(obj.get_daily_plans())

    readable_daily_plans.short_description = 'Планы на каждый день (Список)'

    def readable_daily_plans_detail(self, obj):
        return self.format_daily_plans(obj.get_daily_plans())

    readable_daily_plans_detail.short_description = 'Планы на каждый день'

    def format_daily_plans(self, daily_plans_dict):
        try:
            readable_str = ""
            for date, recipes in daily_plans_dict.items():
                readable_str += f"{date}:\n"
                for recipe in recipes:
                    readable_str += f"  - {recipe}\n"
            return readable_str
        except Exception as e:
            return f"Error: {e}"


admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
