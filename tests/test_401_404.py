from http import HTTPStatus

import pytest

from core.constants import (
    NON_EXISTENT_ID,
    RECIPE_DETAIL_URL,
    RECIPES_URL,
    TAG_DETAIL_URL,
    UNAUTH_AND_AUTH_CLIENTS,
    USER_AVATAR_URL,
    USER_DETAIL_URL,
    USER_LOGOUT_URL,
    USER_ME_URL,
    USER_PASSWORD_URL,
    USER_SUBSCRIBE_URL,
    USER_SUBSCRIPTIONS_URL
)


@pytest.mark.django_db
class TestHTTPErrorResponses:

    ENDPOINTS_METHODS_FIXTURES = [
        (USER_ME_URL, ('get',), None),
        (USER_AVATAR_URL, ('put', 'delete'), None),
        (USER_PASSWORD_URL, ('post',), None),
        (USER_LOGOUT_URL, ('post',), None),
        (USER_SUBSCRIPTIONS_URL, ('get',), None),
        (USER_SUBSCRIBE_URL, ('post', 'delete'), None),
        (RECIPES_URL, ('post',), None),
        (RECIPE_DETAIL_URL, ('patch', 'delete'), 'recipe'),
    ]

    INCORRECT_URL_SEGMENT = 'incorrect'

    @pytest.mark.parametrize(
        'url, method, fixture',
        [
            (url, method, fixture)
            for url, methods, fixture in ENDPOINTS_METHODS_FIXTURES
            for method in methods
        ]
    )
    def test_unauthorized_request_returns_401(
            self,
            url,
            client,
            method,
            request,
            fixture
    ):
        """
        Запрос неавторизованного пользователя к защищённому эндпоинту
        возвращает 401.
        """
        if fixture is not None:
            obj = request.getfixturevalue(fixture)
            url = url.format(id=obj.id)
        response = getattr(client, method)(url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'{method.upper()} {url} без авторизации должен возвращать 401, '
            f'но вернул {response.status_code}'
        )

    @pytest.mark.parametrize(
        'url, fixture_name, method',
        [
            (url, fixture_name, method)
            for (url, fixture_names), methods in {
            (USER_DETAIL_URL.format(id=NON_EXISTENT_ID),
                UNAUTH_AND_AUTH_CLIENTS): ('get',),
            (TAG_DETAIL_URL.format(id=NON_EXISTENT_ID),
                UNAUTH_AND_AUTH_CLIENTS): ('get',),
            (USER_SUBSCRIBE_URL.format(id=NON_EXISTENT_ID),
                ('auth_client',)): ('post', 'delete'),
            (RECIPES_URL.replace(
                RECIPES_URL.split('/')[-2], INCORRECT_URL_SEGMENT
            ), ('auth_client',)): ('post',),
            (RECIPE_DETAIL_URL.format(id=NON_EXISTENT_ID),
                ('auth_client',)): ('patch', 'delete'),
        }.items()
            for fixture_name in fixture_names
            for method in methods
        ],
        indirect=('fixture_name',)
    )
    def test_not_found_returns_404(self, url, fixture_name, method):
        """При запросе несуществующей страницы возвращается 404."""
        response = getattr(fixture_name, method)(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'{method.upper()} {url} должен возвращать 404, '
            f'но вернул {response.status_code}'
        )
