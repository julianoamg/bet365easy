from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from core import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    select_related = ['plan']
    autocomplete_fields = [
        'plan'
    ]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "email", "telegram", "plan", "payment_date", "price", "whatsapp", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name", "telegram", "plan", "price", "payment_date", "whatsapp",)})
    )
    list_display = [
        'email',
        'plan',
        'payment_date',
        'price',
        'get_plan_expiry_date',
        'is_staff',
        'is_superuser',
        'is_active',
    ]
    search_fields = [
        'email'
    ]
    ordering = [
        'email'
    ]

    @admin.display(description='Expira em x dias')
    def get_plan_expiry_date(self, o):
        if not o.plan or not o.payment_date:
            return 'N/D'

        if o.expire_in_days <= 5:
            return format_html(f'''
<span style="color: 000; background: yellow; font-weight: bold; display: inline-block; border-radius: 3px; padding: 5px 10px;">{o.expire_in_days} dias - ATENÇÃO!</span>
            ''')
        return f'{o.expire_in_days} dias'


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'period_in_days'
    ]
    search_fields = [
        'name'
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
        'members_qty',
        'dialog_id',
        'dialog_name',
    ]


@admin.register(models.Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'bot',
        'house',
        'bet',
    ]
    list_filter = [
        'house'
    ]
    search_fields = [
        'user__email',
        'user__name',
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return False

    def has_change_permission(self, request):
        return False
