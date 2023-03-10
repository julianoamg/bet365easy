from django.contrib import admin
from core import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'plan',
        'is_staff',
        'is_superuser',
        'is_active',
    ]
    search_fields = [
        'email'
    ]


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'period_in_days'
    ]


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user'
    ]


@admin.register(models.Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'token',
        'dialog_id',
        'dialog_name',
    ]


@admin.register(models.Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'bot',
        'title',
        'odd',
        'market',
        'game',
        'bet',
        'sent',
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return False

    def has_change_permission(self, request):
        return False