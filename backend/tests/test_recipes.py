from http import HTTPStatus
from typing import Any, Dict, List

import pytest
from core.constants import (RECIPE_DETAIL_URL, RECIPES_URL,
                            UNAUTH_AND_AUTH_CLIENTS)
from logging_setup import logger_setup
from recipes.models import Recipe

from .test_utils import generate_base64_image, list_available

logger = logger_setup()


@pytest.mark.django_db
class TestRecipes:

    RECIPES_FIELDS = (
        "id",
        "tags",
        "author",
        "ingredients",
        "is_favorited",
        "is_in_shopping_cart",
        "name",
        "image",
        "text",
        "cooking_time",
    )

    INVALID_VALUES: Dict[str, List[Any]] = {
        "ingredients": [
            [],
            [{"amount": 5}],  # без id
            [
                {
                    "id": 40,
                }
            ],  # без amount
            [{"id": 40, "amount": 0}],
            [{"id": 40, "amount": -5}],
            [{"id": 40, "amount": "str"}],
        ],
        "tags": [
            [],
        ],
        "name": [
            "",
        ],
        "text": [
            "",
        ],
        "cooking_time": [
            0,
            -5,
            "str",
        ],
        "image": [
            "not base64",
        ],
    }

    @pytest.mark.parametrize("fixture_name",
                             UNAUTH_AND_AUTH_CLIENTS,
                             indirect=True)
    def test_recipes_list_available_to_all(self, fixture_name):
        """Список рецептов доступен всем пользователям."""
        list_available(RECIPES_URL, fixture_name)

    def test_create_recipe_returns_201(
        self,
        auth_client,
        tag,
        tag_2,
        ingredient,
        ingredient_2,
    ):
        """
        Рецепт может быть создан авторизованным пользователем
        и возвращает корректные данные.
        """
        recipe_data = {
            "ingredients": [
                {"id": ingredient.id, "amount": 2},
                {"id": ingredient_2.id, "amount": 50},
            ],
            "tags": [tag.id, tag_2.id],
            "image": (
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
                "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE"
                "0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            ),
            "name": "Тестовый рецепт",
            "text": "Описание тестового рецепта",
            "cooking_time": 15,
        }

        recipes_count_before = Recipe.objects.count()

        response = auth_client.post(
            RECIPES_URL, data=recipe_data, format="json")

        assert response.status_code == HTTPStatus.CREATED, (
            f"POST {RECIPES_URL} должен возвращать 201, "
            f"но вернул {response.status_code}"
        )
        assert (
            Recipe.objects.count() == recipes_count_before + 1
        ), "Количество рецептов должно увеличиваться после создания нового."

        json_data = response.json()

        for field in self.RECIPES_FIELDS:
            assert field in json_data, \
                f"В ответе должно присутствовать поле `{field}`."

        for key in ("name", "text", "cooking_time"):
            assert json_data[key] == recipe_data[key], (
                f"Значение поля `{key}` должно быть {recipe_data[key]!r}, "
                f"но вернулось {json_data[key]!r}."
            )

        # Проверка значений тегов
        assert {
            tag["id"] for tag in json_data["tags"]} == set(
            recipe_data["tags"]), \
            (f'Список тегов должен быть {recipe_data["tags"]}, '
                f'но вернулся {json_data["tags"]}.')

        # Проверка значений ингредиентов
        returned = {(item["id"], item["amount"])
                    for item in json_data["ingredients"]}
        expected = {(item["id"], item["amount"])
                    for item in recipe_data["ingredients"]}
        assert (
            returned == expected
        ), f"Ингредиенты должны быть {expected}, но вернулись {returned}."

    @pytest.mark.parametrize(
        "missing_field",
        ["ingredients", "tags", "image", "name", "text", "cooking_time"],
    )
    def test_create_recipe_missing_required_field_returns_400(
        self,
        auth_client,
        missing_field,
        tag,
        tag_2,
        ingredient,
        ingredient_2,
    ):
        """Создание рецепта без обязательного поля возвращает 400."""
        payload = {
            "ingredients": [
                {"id": ingredient.id, "amount": 2},
                {"id": ingredient_2.id, "amount": 50},
            ],
            "tags": [tag.id, tag_2.id],
            "image": (
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
                "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE"
                "0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            ),
            "name": "Тестовый рецепт",
            "text": "Описание тестового рецепта",
            "cooking_time": 15,
        }
        payload.pop(missing_field)
        response = auth_client.post(RECIPES_URL, data=payload, format="json")
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"POST {RECIPES_URL} без поля `{missing_field}` "
            f"должен возвращать 400, но вернул {response.status_code}"
        )
        assert (
            missing_field in response.json()
        ), f"В ответе должен присутствовать ключ `{missing_field}` с ошибкой."

    @pytest.mark.parametrize(
        "field, invalid_value, method",
        [
            (field, invalid_value, method)
            for field, invalid_list in INVALID_VALUES.items()
            for invalid_value in invalid_list
            for method in ("post", "patch")
        ],
    )
    def test_create_and_update_recipe_with_invalid_field_returns_400(
        self,
        auth_client,
        method,
        field,
        invalid_value,
        tag,
        tag_2,
        ingredient,
        ingredient_2,
        recipe,
    ):
        """
        Создание и обновление рецепта с неправильным значением поля
        возвращает 400.
        """
        payload = {
            "ingredients": [
                {"id": ingredient.id, "amount": 2},
                {"id": ingredient_2.id, "amount": 50},
            ],
            "tags": [tag.id, tag_2.id],
            "image": (
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
                "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE"
                "0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            ),
            "name": "Тестовый рецепт",
            "text": "Описание тестового рецепта",
            "cooking_time": 15,
            field: invalid_value,
        }
        url = (
            RECIPES_URL if method == "post" else RECIPE_DETAIL_URL.format(
                id=recipe.id)
        )
        response = getattr(auth_client, method)(
            url, data=payload, format="json")
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"POST {RECIPES_URL} с неправильным значением поля `{field}` "
            f"должен возвращать 400, но вернул {response.status_code}"
        )
        assert (
            field in response.json()
        ), f"В ответе должен присутствовать ключ `{field}` с ошибкой."

    @pytest.mark.parametrize("fixture_name",
                             UNAUTH_AND_AUTH_CLIENTS,
                             indirect=True)
    def test_recipe_detail_available_to_all(self, fixture_name, recipe):
        """Любой пользователь может получить отдельный рецепт по id."""
        url = RECIPE_DETAIL_URL.format(id=recipe.id)
        response = getattr(fixture_name, "get")(url)

        assert (
            response.status_code == HTTPStatus.OK
        ), f"GET {url} должен возвращать 200, а вернул {response.status_code}"

        json_data = response.json()

        for field in self.RECIPES_FIELDS:
            assert field in json_data, \
                f"В ответе должно присутствовать поле `{field}`."
        assert (
            json_data["id"] == recipe.id
        ), f'В ответе должен быть id={recipe.id}, а не {json_data["id"]}'
        assert json_data["name"] == recipe.name, (
            f"Название рецепта должно быть {recipe.name!r}, "
            f'а вернулось {json_data["name"]!r}.'
        )

    def test_update_recipe_successfully(
            self, auth_client, recipe, ingredient_2, tag_2):
        """Авторизованный пользователь может обновить свой рецепт."""
        url = RECIPE_DETAIL_URL.format(id=recipe.id)

        old_image = getattr(auth_client, "get")(url).json().get("image")

        updated_data = {
            "name": "Обновлённый рецепт",
            "text": "Новое описание рецепта",
            "cooking_time": recipe.cooking_time + 10,
            "tags": [tag_2.id],
            "ingredients": [
                {
                    "id": ingredient_2.id,
                    "amount": 3,
                }
            ],
            "image": generate_base64_image(),
        }

        response = getattr(auth_client, "patch")(
            url, data=updated_data, format="json")
        assert response.status_code == HTTPStatus.OK, (
            f"PATCH {url} должен возвращать 200, "
            f"но вернул {response.status_code!r}"
        )
        json_data = response.json()

        for key in ("name", "text", "cooking_time"):
            assert json_data.get(key) == updated_data[key], (
                f"Поле '{key}' должно быть {updated_data[key]!r} ,"
                f"а вернулось {json_data.get(key)!r}"
            )

        assert json_data.get("tags")[0]["id"] == updated_data["tags"][0], (
            f"Поле 'tags' должно быть {[updated_data['tags'][0]]!r}, "
            f"а вернулось {[t['id'] for t in json_data.get('tags', [])]!r}"
        )
        assert (
            json_data.get("ingredients")[0]["id"]
            == updated_data["ingredients"][0]["id"]
        ), (
            f"Поле 'ingredients[0][id]' "
            f"должно быть {updated_data['ingredients'][0]['id']!r}, "
            f"а вернулось {json_data.get('ingredients')[0]['id']!r}"
        )
        assert (
            json_data.get("ingredients")[0]["amount"]
            == updated_data["ingredients"][0]["amount"]
        ), (
            f"Поле 'ingredients[0][amount]' "
            f"должно быть {updated_data['ingredients'][0]['amount']!r}, "
            f"а вернулось {json_data.get('ingredients')[0]['amount']!r}"
        )

        new_image = json_data.get("image")
        if new_image:
            assert new_image != old_image, (
                f"Поле 'image' должно измениться после обновления, "
                f"старое значение: {old_image!r}, новое: {new_image!r}"
            )

    @pytest.mark.parametrize(
        "method",
        ["patch", "delete"],
    )
    def test_not_author_cant_update_or_delete_recipe(
        self,
        auth_client,
        auth_client_2,
        recipe_with_ingredients_and_tags,
        recipe_with_ingredients_and_tags_2,
        method,
    ):
        """
        Обновление и удаление рецепта не-автором возвращает 403
        и поля не меняются.
        """
        url = RECIPE_DETAIL_URL.format(id=recipe_with_ingredients_and_tags.id)

        before_response_json = getattr(auth_client, "get")(url).json()

        data_to_change = {
            "ingredients": [
                {"id": ing["id"], "amount": ing["amount"]}
                for ing in
                recipe_with_ingredients_and_tags_2.recipe_ingredients.values(
                    "id", "amount"
                )
            ],
            "tags": [tag.id for tag in
                     recipe_with_ingredients_and_tags_2.tags.all()],
            "image": generate_base64_image(),
            "name": recipe_with_ingredients_and_tags_2.name,
            "text": recipe_with_ingredients_and_tags_2.text,
            "cooking_time": recipe_with_ingredients_and_tags_2.cooking_time,
        }
        if method == "patch":
            response = auth_client_2.patch(
                url, data=data_to_change, format="json")
        else:
            response = auth_client_2.delete(url)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f"{method.upper()} {url} должен возвращать 403 для не-автора, "
            f"но вернул {response.status_code}"
        )

        after_response_json = getattr(auth_client, "get")(url).json()

        for key in ("name", "text", "cooking_time", "image"):
            assert after_response_json[key] == before_response_json[key], (
                f"Поле {key!r} изменилось: "
                f"было {before_response_json[key]!r}, "
                f"стало {after_response_json[key]!r}"
            )

        assert [
            (ing["id"], ing["amount"]) for ing in
            after_response_json["ingredients"]
        ] == [
            (ing["id"], ing["amount"]) for ing in
            before_response_json["ingredients"]
        ], "Список ингредиентов изменился!"

        assert sorted([t["id"] for t in
                       after_response_json["tags"]]) == sorted(
            [t["id"] for t in before_response_json["tags"]]
        ), "Список тегов изменился!"
