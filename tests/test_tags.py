from http import HTTPStatus

import pytest

from core.constants import TAG_DETAIL_URL, TAGS_URL


@pytest.mark.django_db
class TestTags:

    @pytest.mark.parametrize('client_name', ('client', 'auth_client'))
    def test_tags_list_available(self, client_name, client, auth_client):
        """Список тегов доступен всем пользователям."""
        api_client = {
            'client': client,
            'auth_client': auth_client,
        }.get(client_name)
        response = api_client.get(TAGS_URL)

        assert response.status_code == HTTPStatus.OK, (
            f'GET {TAGS_URL} должен возвращать 200, '
            f'но вернул {response.status_code}'
        )
        assert 'results' in response.json(), (
            'Ответ должен содержать ключ "results"'
        )
        assert isinstance(response.json().get('results'), list), (
            'Значение по ключу "results" должно быть списком'
        )

    @pytest.mark.parametrize('client_name', ('client', 'auth_client'))
    def test_tag_detail_available(
        self, client_name, client, auth_client, tag
    ):
        """Любой пользователь может получить тег по id."""
        api_client = {
            'client': client,
            'auth_client': auth_client,
        }.get(client_name)
        url = TAG_DETAIL_URL.format(id=tag.id)
        response = api_client.get(url)

        assert response.status_code == HTTPStatus.OK, (
            f'GET {url} должен возвращать 200, '
            f'но вернул {response.status_code}'
        )

        data = response.json()

        for field in ('id', 'name', 'slug'):
            assert field in data, f'В ответе должно быть поле "{field}"'

        assert data.get('id') == tag.id, 'Неверный id тега.'
        assert data.get('name') == tag.name, 'Неверное имя тега.'
        assert data.get('slug') == tag.slug, 'Неверный slug тега.'
