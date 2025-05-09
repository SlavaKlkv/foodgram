from django.contrib import admin

from .models import Subscription, User

admin.site.empty_value_display = 'Не указано'


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff'
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_display_links = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
