from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)
from users.views import UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
routes = [
    ('users', UserViewSet),
    ('tags', TagViewSet),
    ('ingredients', IngredientViewSet),
    ('recipes', RecipeViewSet),
]
for prefix, viewset in routes:
    router_v1.register(prefix, viewset, basename=prefix)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
