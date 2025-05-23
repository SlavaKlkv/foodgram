from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from core.constants import (
    USER_AVATAR_URL,
    USER_LOGOUT_URL,
    USER_ME_URL,
    USER_PASSWORD_URL,
    USER_SUBSCRIBE_URL,
    USER_SUBSCRIPTIONS_URL
)


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
def test_unauthorized_request_returns_401(url, method):
    """
    Запрос неавторизованного пользователя к защищённому эндпоинту
    возвращает 401.
    """
    response = getattr(APIClient(), method)(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        f'{method.upper()} {url} без авторизации должен возвращать 401.'
    )
