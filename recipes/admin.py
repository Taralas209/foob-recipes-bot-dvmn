from django.contrib import admin
from .models import Recipes, Category, Ingredients,User, SubscriptionPlan
import json

admin.site.register(Recipes)
admin.site.register(Category)
admin.site.register(Ingredients)

class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'get_plan', 'get_start_date', 'get_end_date')

    def get_plan(self, obj):
        if obj.current_subscription_plan:
            return obj.current_subscription_plan.plan_choice
        return 'Нет плана'

    get_plan.short_description = 'План'

    def get_start_date(self, obj):
        if obj.current_subscription_plan:
            return obj.current_subscription_plan.start_date
        return 'Нет даты начала'

    get_start_date.short_description = 'Дата начала'

    def get_end_date(self, obj):
        if obj.current_subscription_plan:
            return obj.current_subscription_plan.end_date
        return 'Нет даты окончания'

    get_end_date.short_description = 'Дата окончания'

admin.site.register(User, UserAdmin)

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
