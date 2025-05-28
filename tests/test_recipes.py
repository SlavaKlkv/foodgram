# from http import HTTPStatus
#
# import pytest
#
# from core.constants import RECIPES_URL
# from recipes.models import Recipe
#
#
# @pytest.mark.django_db
# class TestRecipes:
#
#     def test_get_recipes_returns_200(self, client):
#         """Любой пользователь может получить список рецептов."""
#         response = client.get(RECIPES_URL)
#
#         assert response.status_code == HTTPStatus.OK, (
#             f'GET {RECIPES_URL} должен возвращать 200, '
#             f'но вернул {response.status_code}'
#         )
#
#     def test_create_recipe_returns_201(self, auth_client):
#         recipe_data = {
#             'ingredients': [
#                 {'id': 1, 'amount': 100},
#                 {'id': 2, 'amount': 200}
#             ],
#             'tags': [1, 2],
#             'image': (
#                 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
#                 'AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE'
#                 '0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
#             ),
#             'name': 'Тестовый рецепт',
#             'text': 'Описание тестового рецепта',
#             'cooking_time': 15
#         }
#
#         recipes_count_before = Recipe.objects.count()
#
#         response = auth_client.post(
#             RECIPES_URL,
#             data=recipe_data,
#         )
#
#         recipes_count_after = Recipe.objects.count()
#         assert response.status_code == HTTPStatus.CREATED, (
#             f'POST {RECIPES_URL} должен возвращать 201, '
#             f'но вернул {response.status_code}'
#         )
#         assert recipes_count_after == recipes_count_before + 1, (
#             'Количество рецептов должно увеличиваться после создания нового.'
#         )