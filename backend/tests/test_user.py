import base64
from http import HTTPStatus
from typing import (
    Any,
    Dict,
    List,
    Tuple
)

import pytest
from core.constants import (
    UNAUTH_AND_AUTH_CLIENTS,
    USER_AVATAR_URL,
    USER_DETAIL_URL,
    USER_LOGIN_URL,
    USER_LOGOUT_URL,
    USER_ME_URL,
    USER_PASSWORD_URL,
    USERS_URL,
)
from PIL import Image

from users.models import User
from .test_utils import list_available

INVALID_VALUES: Dict[str, List[Any]] = {
    'email': [
        'not an email'
    ],
    'username': [
        '',
        '   ',
        '!!!invalid###'
    ]
}

PARAMS: List[Tuple[str, Any]] = [
    (field, invalid_value)
    for field, invalid_list in INVALID_VALUES.items()
    for invalid_value in invalid_list
]

def add_avatar(auth_client, tmp_path, color='red'):
    image_path = tmp_path / 'avatar.png'
    image = Image.new('RGB', (100, 100), color=color)
    image.save(image_path, format='PNG')
    with open(image_path, 'rb') as img:
        base64_data = (
            'data:image/png;base64,' +
            base64.b64encode(img.read()).decode('utf-8')
        )
    return auth_client.put(
        USER_AVATAR_URL, data={'avatar': base64_data}, format='json'
    )

@pytest.mark.django_db(transaction=True)
class TestUsers:

    def test_get_users_list_unauthorized(self, client):
        """Список пользователей доступен без авторизации."""
        list_available(USERS_URL, client)

    def test_register_user_successfully(self, client):
        """
        Новый пользователь может зарегистрироваться
        и возвращаются корректные данные.
        """
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'strongpassword123'
        }
        initial_count = User.objects.count()

        response = client.post(USERS_URL, data=data)

        assert response.status_code == HTTPStatus.CREATED, (
            f'POST {USERS_URL} с валидными данными должен возвращать 201, '
            f'но вернул {response.status_code}'
        )
        assert User.objects.count() == initial_count + 1, (
            'Количество пользователей должно увеличиваться '
            'после регистрации нового.'
        )

        json_data = response.json()

        for field in ('id', 'email', 'username', 'first_name', 'last_name'):
            assert field in json_data, \
                f'В ответе должно присутствовать поле `{field}`.'

        for key, value in data.items():
            if key == 'password':
                continue
            assert json_data.get(key) == value, (
                f'Значение поля `{key}` должно быть `{value}`, '
                f'но вернулось `{json_data.get(key)}`.'
            )

    @pytest.mark.parametrize('missing_field', [
        'email', 'username', 'first_name', 'last_name', 'password'
    ])
    def test_register_user_missing_required_field_returns_400(
            self,
            client,
            missing_field
    ):
        """Регистрация без обязательного поля возвращает 400."""
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123'
        }
        data.pop(missing_field)
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} без поля `{missing_field}` '
            f'должен возвращать 400, но вернул {response.status_code}'
        )
        assert missing_field in response.json(), (
            f"В ответе должен присутствовать ключ `{missing_field}` с ошибкой."
        )

    @pytest.mark.parametrize('field, invalid_value', PARAMS)
    def test_register_user_with_invalid_field_returns_400(
            self,
            client,
            field,
            invalid_value
    ):
        """Регистрация с неправильным значением поля возвращает 400."""
        data = {
            'email': 'user@example.com',
            'username': 'validuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123',
            field: invalid_value
        }
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} с неправильным значением поля `{field}` '
            f'должен возвращать 400, но вернул {response.status_code}'
        )
        assert field in response.json(), (
            f"В ответе должен присутствовать ключ `{field}` с ошибкой."
        )

    @pytest.mark.parametrize('field', ['email', 'username'])
    def test_register_user_with_duplicate_field_returns_400(self,
                                                            client,
                                                            user,
                                                            field):
        """Регистрация с уже занятым email или username возвращает 400."""
        data = {
            'email': 'unique@example.com',
            'username': 'uniqueuser',
            'first_name': 'A',
            'last_name': 'B',
            'password': 'strongpass123',
            field: getattr(user, field)
        }
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} с уже занятым `{field}` должен возвращать 400, '
            f'но вернул {response.status_code}'
        )

    @pytest.mark.parametrize(
        'url, fixture_name',
        [
            (url, fixture_name)
            for url, clients in {
            USER_DETAIL_URL: UNAUTH_AND_AUTH_CLIENTS,
            USER_ME_URL: ('auth_client',)
        }.items()
            for fixture_name in clients
        ],
    indirect=('fixture_name',)
    )
    def test_user_profile_available_and_returns_correct_data(
            self,
            url,
            fixture_name,
            user,
    ):
        """
        Любой пользователь может получить профиль другого по id
        с корректными данными и авторизованному доступен свой.
        """
        resolved_url = url.format(id=user.id) if '{id}' in url else url
        response = getattr(fixture_name, 'get')(resolved_url)

        assert response.status_code == HTTPStatus.OK, (
            f'GET {url} должен возвращать 200, '
            f'но вернул {response.status_code}'
        )

        json_data = response.json()
        expected_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )
        for field in expected_fields:
            assert field in json_data, f'В ответе должно быть поле `{field}`.'

        assert json_data.get('id') == user.id, 'Неверный id.'
        assert json_data.get('email') == user.email, 'Неверный email.'
        assert json_data.get('username') == user.username, 'Неверный username.'
        assert json_data.get('first_name') == user.first_name, \
            'Неверный first_name.'
        assert json_data.get('last_name') == user.last_name, \
            'Неверный last_name.'
        assert json_data.get('is_subscribed') is False, \
            'Поле is_subscribed должно быть False.'


    def test_add_avatar_successfully(self, auth_client, tmp_path):
        """Пользователь может добавить аватар."""

        response = add_avatar(auth_client, tmp_path)

        assert 'avatar' in response.json(),\
            'Ответ должен содержать поле avatar.'
        assert response.json()['avatar'], 'Поле avatar не должно быть пустым.'
        assert response.status_code == HTTPStatus.OK, (
            f'PUT {USER_AVATAR_URL} с валидным изображением '
            f'должен возвращать 200, но вернул {response.status_code}'
        )

    def test_delete_avatar_successfully(self, auth_client, tmp_path):
        """Пользователь может удалить аватар."""

        add_avatar(auth_client, tmp_path, color='blue')
        assert auth_client.delete(

            USER_AVATAR_URL).status_code == HTTPStatus.NO_CONTENT, (
            f'DELETE {USER_AVATAR_URL} должен возвращать 204.'
        )
        response = auth_client.get(USER_ME_URL)
        assert response.status_code == HTTPStatus.OK, (
            f'GET {USER_ME_URL} должен возвращать 200 после удаления аватара, '
            f'но вернул {response.status_code}'
        )
        assert response.json()['avatar'] is None, (
            'После удаления аватара это поле должно быть пустым.'
        )

    @pytest.mark.parametrize('payload', [
        {}, {'avatar': ''}, {'avatar': 'invalid_format'}
    ])
    def test_add_avatar_returns_400_on_invalid_data(
            self, auth_client, payload
    ):
        """Передача невалидных данных в поле avatar
        или их отсутствие возвращает 400.
        """
        response = auth_client.put(
            USER_AVATAR_URL, data=payload, format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'PUT {USER_AVATAR_URL} с данными {payload} должен возвращать 400,'
            f' но вернул {response.status_code}'
        )

    def test_change_password_successfully(self, auth_client):
        """Пользователь может успешно сменить пароль."""
        payload = {
            'current_password': '1234567',
            'new_password': 'new_secure_password456'
        }
        response = auth_client.post(USER_PASSWORD_URL, data=payload)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Успешная смена пароля должна возвращать 204, '
            f'но вернула {response.status_code}'
        )

    @pytest.mark.parametrize('payload', [
        {},  # оба поля отсутствуют
        {'new_password': 'newpass123'},  # отсутствует current_password
        {'current_password': '1234567'},  # отсутствует new_password
        {'current_password': 'wrongpass',
         'new_password': 'newpass123'},  # неверный текущий пароль
    ])
    def test_change_password_returns_400_on_invalid_data(
            self, auth_client, payload
    ):
        """Передача невалидных данных при смене пароля возвращает 400."""
        response = auth_client.post(USER_PASSWORD_URL, data=payload)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USER_PASSWORD_URL} с данными {payload} '
            f'должен возвращать 400, но вернул {response.status_code}'
        )

    def test_token_login_successfully(self, client, user):
        """Пользователь может получить токен при входе с валидными данными."""
        response = client.post(USER_LOGIN_URL, data={
            'email': user.email,
            'password': user.plaintext_password
        })
        assert response.status_code == HTTPStatus.OK, (
            f'POST {USER_LOGIN_URL} ' 
            f'должен возвращать 200 при корректных данных, '
            f'но вернул {response.status_code}'
        )
        assert 'auth_token' in response.json(), (
            'Ответ должен содержать поле auth_token.'
        )

    def test_token_logout_successfully(self, auth_client):
        """Пользователь может выйти (удалить токен)."""
        response = auth_client.post(USER_LOGOUT_URL)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'POST {USER_LOGOUT_URL} '
            f'должен возвращать 204 при успешном выходе, '
            f'но вернул {response.status_code}'
        )
