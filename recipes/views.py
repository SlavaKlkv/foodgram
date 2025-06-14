from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from core.filters import IngredientFilter, RecipeFilter
from core.mixins import CustomGetObjectMixin
from core.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Ingredient,
    Recipe,
    Tag
)
from recipes.serializers import (
    IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)


class TagViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    object = 'тега'


class IngredientViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    object = 'ингредиента'


class RecipeViewSet(CustomGetObjectMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    object = 'рецепта'

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()


    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        recipe = self.get_object()
        return Response(
            {'short-link': f'{settings.SITE_URL}/s/{recipe.id}'}
        )
