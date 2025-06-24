from http import HTTPStatus

import pytest
from core.constants import (INGREDIENT_DETAIL_URL, INGREDIENTS_URL,
                            TAG_DETAIL_URL, TAGS_URL, UNAUTH_AND_AUTH_CLIENTS)

from .test_utils import list_available


@pytest.mark.django_db
class TestTagsAndIngredients:

    @pytest.mark.parametrize(
        "url, fixture_name",
        [
            (url, fixture_name)
            for url, clients in {
                TAGS_URL: UNAUTH_AND_AUTH_CLIENTS,
                INGREDIENTS_URL: UNAUTH_AND_AUTH_CLIENTS,
            }.items()
            for fixture_name in clients
        ],
        indirect=("fixture_name",),
    )
    def test_ingredient_and_tags_list_available(self, url, fixture_name):
        """Списки тегов и ингредиентов доступны всем пользователям."""
        list_available(url, fixture_name)

    @pytest.mark.parametrize(
        "url, fixture_name",
        [
            (url, fixture_name)
            for url, clients in {
                TAG_DETAIL_URL: UNAUTH_AND_AUTH_CLIENTS,
                INGREDIENT_DETAIL_URL: UNAUTH_AND_AUTH_CLIENTS,
            }.items()
            for fixture_name in clients
        ],
        indirect=("fixture_name",),
    )
    def test_detail_available_and_returns_correct_data(
        self,
        url,
        fixture_name,
        tag,
        ingredient,
    ):
        """
        Любой пользователь может получить тег или ингредиент по его id
        с корректными данными.
        """
        key = "tags" if "tags" in url else "ingredients"
        mapping = {
            "tags": {
                "fixture": tag,
                "field_name": "slug",
                "object_name": "тега",
            },
            "ingredients": {
                "fixture": ingredient,
                "field_name": "measurement_unit",
                "object_name": "ингредиента",
            },
        }
        context = mapping.get(f"{key}")
        obj = context.get("fixture")
        field_name = context.get("field_name")
        field_value = getattr(obj, field_name)

        resolved_url = url.format(id=obj.id) if "{id}" in url else url
        response = getattr(fixture_name, "get")(resolved_url)

        assert response.status_code == HTTPStatus.OK, (
            f"GET {url} должен возвращать 200, "
            f"но вернул {response.status_code}"
        )

        json_data = response.json()

        for field in ("id", "name", field_name):
            assert field in json_data, f'В ответе должно быть поле "{field}"'
        assert json_data.get(
            "id") == obj.id, f'Неверный id {context["object_name"]}.'
        assert (
            json_data.get("name") == obj.name
        ), f'Неверное имя {context["object_name"]}.'
        assert (
            json_data.get(field_name) == field_value
        ), f'Поле {field_name} {context["object_name"]} некорректно.'
