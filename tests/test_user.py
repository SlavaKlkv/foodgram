import base64
from http import HTTPStatus

import pytest
from PIL import Image
from rest_framework.test import APIClient

from core.constants import (
    USER_AVATAR_URL,
    USER_DETAIL_URL,
    USER_LOGIN_URL, USER_LOGOUT_URL, USER_ME_URL,
    USER_PASSWORD_URL,
    USERS_URL,
)


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

    def test_get_users_list_unauthorized(self):
        """Список пользователей доступен без авторизации."""
        response = APIClient().get(USERS_URL)
        assert response.status_code == HTTPStatus.OK, (
            f'GET {USERS_URL} должен быть доступен без токена.'
        )
        assert isinstance(response.json().get('results'), list), \
            'Ожидается, что ответ содержит список пользователей.'

    def test_register_user_successfully(self):
        """Новый пользователь может зарегистрироваться."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'strongpassword123'
        }
        response = APIClient().post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'POST {USERS_URL} с валидными данными должен возвращать 201.'
        )
        json_data = response.json()
        for field in ('id', 'email', 'username', 'first_name', 'last_name'):
            assert field in json_data, \
                f'В ответе должно присутствовать поле `{field}`.'

    @pytest.mark.parametrize('missing_fields', [
        'email', 'username', 'first_name', 'last_name', 'password'
    ])
    def test_register_user_missing_required_field_returns_400(
            self, missing_fields
    ):
        """Регистрация без обязательного поля возвращает 400."""
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123'
        }
        data.pop(missing_fields)
        response = APIClient().post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} без поля `{missing_fields}` должен возвращать 400.'
        )

    @pytest.mark.parametrize('field, invalid_value', [
        ('email', 'not-an-email'),
        ('username', ''),
        ('username', '   '),
        ('username', '!!!invalid###'),
    ])
    def test_register_user_with_invalid_field_returns_400(
            self, field, invalid_value
    ):
        """Регистрация с невалидным значением поля возвращает 400."""
        data = {
            'email': 'user@example.com',
            'username': 'validuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123',
            field: invalid_value
        }
        response = APIClient().post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} с невалидным значением поля `{field}` '
            f'должен возвращать 400.'
        )

    @pytest.mark.parametrize('field', ['email', 'username'])
    def test_register_user_with_duplicate_field_returns_400(self, user, field):
        """Регистрация с уже занятым email или username возвращает 400."""
        data = {
            'email': 'unique@example.com',
            'username': 'uniqueuser',
            'first_name': 'A',
            'last_name': 'B',
            'password': 'strongpass123',
            field: getattr(user, field)
        }
        response = APIClient().post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} с уже занятым `{field}` должен возвращать 400.'
        )

    def test_user_profile_accessible_to_all(self, auth_client, user):
        """Профиль пользователя доступен всем."""
        url = USER_DETAIL_URL.format(id=user.id)

        for response, label in (
            (APIClient().get(url), 'неавторизованного'),
            (auth_client.get(url), 'авторизованного'),
        ):
            assert response.status_code == HTTPStatus.OK, (
                f'GET {url} должен возвращать 200 для {label} пользователя.'
            )
            for field in (
                'id', 'username', 'email', 'first_name', 'last_name',
                'is_subscribed', 'avatar'
            ):
                assert field in response.json(), (
                    f'В ответе должно быть поле `{field}`.'
                )

    def test_user_profile_not_found_returns_404(self, user):
        """Запрос профиля несуществующего пользователя возвращает 404."""
        response = APIClient().get(
            USER_DETAIL_URL.format(id=user.id + 1000000)
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Запрос профиля пользователя с несуществующим id '
            'должен возвращать 404.'
        )

    def test_get_current_user_profile(self, auth_client, user):
        """Пользователь может получить свой профиль."""
        response = auth_client.get(USER_ME_URL)
        assert response.status_code == HTTPStatus.OK, (
            f'GET {USER_ME_URL} должен возвращать 200 '
            f'для авторизованного пользователя.'
        )
        json_data = response.json()
        for field in (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        ):
            assert field in json_data, f'В ответе должно быть поле `{field}`.'
        assert json_data['id'] == user.id,\
            'ID пользователя должен совпадать с авторизованным.'

    def test_add_avatar_successfully(self, auth_client, tmp_path):
        """Пользователь может добавить аватар."""

        response = add_avatar(auth_client, tmp_path)

        assert 'avatar' in response.json(),\
            'Ответ должен содержать поле avatar.'
        assert response.json()['avatar'], 'Поле avatar не должно быть пустым.'
        assert response.status_code == HTTPStatus.OK, (
            f'PUT {USER_AVATAR_URL} с валидным изображением '
            'должен возвращать 200.'
        )

    def test_delete_avatar_successfully(self, auth_client, tmp_path):
        """Пользователь может удалить аватар."""

        add_avatar(auth_client, tmp_path, color='blue')
        assert auth_client.delete(

            USER_AVATAR_URL).status_code == HTTPStatus.NO_CONTENT, (
            f'DELETE {USER_AVATAR_URL} должен возвращать 204.'
        )
        response = auth_client.get(USER_ME_URL)
        assert response.status_code == HTTPStatus.OK
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
            f'PUT {USER_AVATAR_URL} с данными {payload} должен возвращать 400.'
        )

    def test_change_password_successfully(self, auth_client):
        """Пользователь может успешно сменить пароль."""
        payload = {
            'current_password': '1234567',
            'new_password': 'new_secure_password456'
        }
        response = auth_client.post(USER_PASSWORD_URL, data=payload)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Успешная смена пароля должна возвращать 204.'
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
            'должен возвращать 400.'
        )

    def test_token_login_successfully(self, user):
        """Пользователь может получить токен при входе с валидными данными."""
        response = APIClient().post(USER_LOGIN_URL, data={
            'email': user.email,
            'password': user.plaintext_password
        })
        assert response.status_code == HTTPStatus.OK, (
            f'POST {USER_LOGIN_URL} '
            'должен возвращать 200 при корректных данных.'
        )
        assert 'auth_token' in response.json(), (
            'Ответ должен содержать поле auth_token.'
        )

    def test_token_logout_successfully(self, auth_client):
        """Пользователь может выйти (удалить токен)."""
        response = auth_client.post(USER_LOGOUT_URL)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'POST {USER_LOGOUT_URL} '
            'должен возвращать 204 при успешном выходе.'
        )
