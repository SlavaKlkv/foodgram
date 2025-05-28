import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

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