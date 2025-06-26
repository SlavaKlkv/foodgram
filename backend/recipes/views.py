from django.conf import settings
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from core.filters import IngredientFilter, RecipeFilter
from core.mixins import CustomGetObjectMixin
from core.permissions import IsAuthorOrReadOnly
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)


class TagViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    object = "Тег"


class IngredientViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    object = "Ингредиент"


class RecipeViewSet(CustomGetObjectMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    # pagination_class = CustomLimitOffsetPagination
    object = "Рецепт"

    ACTION_CASES = {
        "shopping_cart": {
            "prepositional": "в списке покупок",
            "genitive": "из списка покупок",
        },
        "favorite": {
            "prepositional": "в избранном",
            "genitive": "из избранного"},
    }

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        filter_params = (
            ("is_in_shopping_cart", "is_in_shopping_cart__user"),
            ("is_favorited", "is_favorited__user"),
        )

        for param, filter_expr in filter_params:
            value = self.request.query_params.get(param)
            if value in ("1", "true", "True"):
                if user.is_authenticated:
                    queryset = queryset.filter(**{filter_expr: user})
                else:
                    return queryset.none()

        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        if self.action in ("shopping_cart", "favorite"):
            return (IsAuthenticated(),)
        if self.request.method in ("PATCH", "DELETE"):
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()

    @action(detail=True, methods=("get",), url_path="get-link")
    def get_link(self, request, *args, **kwargs):
        recipe = self.get_object()
        return Response({"short-link": f"{settings.SITE_URL}/s/{recipe.id}"})

    def _user_recipe_action(self, request, model, action_cases):
        """Общий метод для добавления/удаления рецепта."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            _, created = model.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                return Response(
                    {"detail": "Рецепт "
                               f'уже {action_cases["prepositional"]}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RecipeShortSerializer(
                recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            deleted, _ = model.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(
                    {"success":
                        "Рецепт " f'удалён {action_cases["genitive"]}.'},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"detail": "Рецепта "
                           f'не было {action_cases["prepositional"]}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта в/из список(ка) покупок."""
        return self._user_recipe_action(
            request, ShoppingCart, self.ACTION_CASES["shopping_cart"]
        )

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта в/из избранное(ого)."""
        return self._user_recipe_action(
            request, Favorite, self.ACTION_CASES["favorite"]
        )

    @action(detail=False, methods=("get",),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        from recipes.utils import generate_shopping_list

        txt_content = generate_shopping_list(request.user)
        response = HttpResponse(txt_content, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
