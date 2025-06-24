from django.contrib import admin
from users.models import Subscription, User

admin.site.empty_value_display = "Не указано"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "is_staff")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    list_display_links = ("user", "author")
