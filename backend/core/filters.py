import django_filters
from django.db.models import Case, IntegerField, Q, When
from logging_setup import logger_setup
from recipes.models import Ingredient, Recipe

logger = logger_setup()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_name(self, queryset, name, value):
        return (
            queryset.filter(Q(name__istartswith=value)
                            | Q(name__icontains=value))
            .annotate(
                priority=Case(
                    When(name__istartswith=value, then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            )
            .order_by("priority", "name")
        )


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.filters.AllValuesMultipleFilter(
        field_name="tags__slug")

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
        )
