from http import HTTPStatus

import pytest

from core.constants import (NON_EXISTENT_ID, TAG_DETAIL_URL, USER_AVATAR_URL,
                            USER_DETAIL_URL, USER_LOGOUT_URL, USER_ME_URL,
                            USER_PASSWORD_URL, USER_SUBSCRIBE_URL,
                            USER_SUBSCRIPTIONS_URL)


@pytest.mark.parametrize(
    'url, method',
    [
        (url, method)
        for url, methods in {
            USER_ME_URL: ('get',),
            USER_AVATAR_URL: ('put', 'delete'),
            USER_PASSWORD_URL: ('post',),
            USER_LOGOUT_URL: ('post',),
            USER_SUBSCRIPTIONS_URL: ('get',),
            USER_SUBSCRIBE_URL: ('post', 'delete')
        }.items()
        for method in methods
    ]
)
def test_unauthorized_request_returns_401(url, client, method):
    """
    Запрос неавторизованного пользователя к защищённому эндпоинту
    возвращает 401.
    """
    response = getattr(client, method)(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        f'{method.upper()} {url} без авторизации должен возвращать 401, '
        f'но вернул {response.status_code}'
    )

@pytest.mark.parametrize(
    'url, client_name, method',
    [
        (url, client_name, method)
        for (url, client_name), methods in {
            (USER_DETAIL_URL.format(id=NON_EXISTENT_ID), 'client'): ('get',),
            (TAG_DETAIL_URL.format(id=NON_EXISTENT_ID), 'client'): ('get',),
            (USER_SUBSCRIBE_URL.format(id=NON_EXISTENT_ID), 'auth_client'):
                ('post', 'delete')
        }.items()
        for method in methods
    ],
    indirect=('client_name',)
)
@pytest.mark.django_db
def test_not_found_returns_404(url, client_name, method):
    """При запросе несуществующей страницы возвращается 404."""
    response = getattr(client_name, method)(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'{method.upper()} {url} должен возвращать 404, '
        f'но вернул {response.status_code}'
    )
