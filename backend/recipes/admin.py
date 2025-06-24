from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

admin.site.empty_value_display = "Не указано"


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorites_count")
    search_fields = ("name", "author")
    list_filter = ("tags",)
    inlines = (RecipeIngredientInline,)

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return obj.favorited_by.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


admin.site.register(RecipeIngredient)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
