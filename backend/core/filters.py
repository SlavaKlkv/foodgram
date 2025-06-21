import django_filters
from django.db.models import (
    Case,
    IntegerField,
    Q,
    When
)

from logging_setup import logger_setup

logger = logger_setup()

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            priority=Case(
                When(name__istartswith=value, then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('priority', 'name')

class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def _filter_by_user_relation(self, queryset, related_field, value):
        user = self.request.user

        if user.is_anonymous:
            return queryset.none() if value else queryset
        filter_expr = {f'{related_field}__user': user}
        if value:
            return queryset.filter(**filter_expr)
        else:
            return queryset.exclude(**filter_expr)

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_by_user_relation(
            queryset,
            'favorited_by',
            value
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_by_user_relation(
            queryset,
            'in_shopping_carts',
            value
        )