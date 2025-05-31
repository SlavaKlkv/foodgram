from http import HTTPStatus

import pytest

from core.constants import (
    INGREDIENT_DETAIL_URL,
    INGREDIENTS_URL,
    TAG_DETAIL_URL,
    TAGS_URL,
    UNAUTH_AND_AUTH_CLIENTS
)


@pytest.mark.django_db
class TestTagsAndIngredients:

    @pytest.mark.parametrize(
        'url, client_name',
        [
            (url, client_name)
            for url, clients in {
                TAGS_URL: UNAUTH_AND_AUTH_CLIENTS,
                INGREDIENTS_URL: UNAUTH_AND_AUTH_CLIENTS,
            }.items()
            for client_name in clients
        ],
    )
    def test_list_available(self, url, client_name, request):
        """Списки тегов и ингредиентов доступны всем пользователям."""

        response = request.getfixturevalue(client_name).get(url)

        assert response.status_code == HTTPStatus.OK, (
            f'GET {url} должен возвращать 200, '
            f'но вернул {response.status_code}'
        )
        assert 'results' in response.json(), (
            f'Ответ {url} должен содержать ключ "results"'
        )
        assert isinstance(response.json().get('results'), list), (
            f'Значение ключа "results" из {url} должно быть списком'
        )

    @pytest.mark.parametrize(
        'url, client_name',
        [
            (url, client_name)
            for url, clients in {
                TAG_DETAIL_URL.format(id=1): UNAUTH_AND_AUTH_CLIENTS,
                INGREDIENT_DETAIL_URL.format(id=1): UNAUTH_AND_AUTH_CLIENTS,
            }.items()
            for client_name in clients
        ]
    )
    def test_detail_available(
            self,
            url,
            client_name,
            request,
            tag,
            ingredient,
    ):
        """Любой пользователь может получить тег или ингредиент по его id."""
        response = request.getfixturevalue(client_name).get(url)

        assert response.status_code == HTTPStatus.OK, (
            f'GET {url} должен возвращать 200, '
            f'но вернул {response.status_code}'
        )

        data = response.json()
        key = 'ingredients' if 'ingredients' in url else 'tags'
        mapping = {
            'tags': {
                'fixture': tag,
                'field_name': 'slug',
                'object_name': 'тега',
            },
            'ingredients': {
                'fixture': ingredient,
                'field_name': 'measurement_unit',
                'object_name': 'ингредиента',
            }
        }
        context = mapping[key]
        obj = context['fixture']
        field_name = context['field_name']
        field_value = getattr(obj, field_name)

        for field in ('id', 'name', field_name):
            assert field in data, f'В ответе должно быть поле "{field}"'
        assert data.get('id') == obj.id,\
            f'Неверный id {context["object_name"]}.'
        assert data.get('name') == obj.name,\
            f'Неверное имя {context["object_name"]}.'
        assert data.get(field_name) == field_value,\
            f'Поле {field_name} {context["object_name"]} некорректно.'
