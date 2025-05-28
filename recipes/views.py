from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from core.filters import RecipeFilter
from core.mixins import CustomGetObjectMixin
from core.permissions import IsAuthorOrReadOnly
from recipes.models import Recipe, Tag
from recipes.serializers import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)


class TagViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    not_found_detail = 'Такого тега не существует.'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer


    @action(detail=True, methods=('get',))
    def get_link(self):
        recipe = self.get_object()
        return Response(
            {'short-link': f'{settings.SITE_URL}/s/{recipe.id}'}
        )
