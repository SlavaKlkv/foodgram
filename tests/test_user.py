import base64
from http import HTTPStatus

import pytest
from PIL import Image

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

    def test_get_users_list_unauthorized(self, client):
        """Список пользователей доступен без авторизации."""
        response = client.get(USERS_URL)
        assert response.status_code == HTTPStatus.OK, (
            f'GET {USERS_URL} должен быть доступен без токена, '
            f'но вернул {response.status_code}'
        )
        assert "results" in response.json(), \
            'Ответ должен содержать ключ "results"'
        assert isinstance(response.json().get('results'), list), \
            'Значение по ключу "results" должно быть списком'

    def test_register_user_successfully(self, client):
        """Новый пользователь может зарегистрироваться."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'strongpassword123'
        }
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'POST {USERS_URL} с валидными данными должен возвращать 201, '
            f'но вернул {response.status_code}'
        )
        json_data = response.json()
        for field in ('id', 'email', 'username', 'first_name', 'last_name'):
            assert field in json_data, \
                f'В ответе должно присутствовать поле `{field}`.'

    @pytest.mark.parametrize('missing_fields', [
        'email', 'username', 'first_name', 'last_name', 'password'
    ])
    def test_register_user_missing_required_field_returns_400(
            self,
            client,
            missing_fields
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
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} без поля `{missing_fields}` '
            f'должен возвращать 400, но вернул {response.status_code}'
        )

    @pytest.mark.parametrize('field, invalid_value', [
        ('email', 'not-an-email'),
        ('username', ''),
        ('username', '   '),
        ('username', '!!!invalid###'),
    ])
    def test_register_user_with_invalid_field_returns_400(
            self,
            client,
            field,
            invalid_value
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
        response = client.post(USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST {USERS_URL} с невалидным значением поля `{field}` '
            f'должен возвращать 400, но вернул {response.status_code}'
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

    @pytest.mark.parametrize('url_name, is_self', [
        (lambda user: USER_DETAIL_URL.format(id=user.id), False),
        (lambda user: USER_ME_URL, True),
    ])
    def test_user_profile_returns_correct_data(
            self,
            auth_client,
            client,
            user,
            url_name,
            is_self
    ):
        """
        Профиль пользователя доступен всем и возвращает корректные данные.
        """
        if is_self:
            clients = (auth_client,)
        else:
            clients = (client, auth_client)

        for api_client in clients:
            url = url_name(user)
            response = api_client.get(url)
            assert response.status_code == HTTPStatus.OK, (
                f'GET {url} должен возвращать 200, '
                f'но вернул {response.status_code}'
            )
            json_data = response.json()
            expected_fields = (
                'email', 'id', 'username', 'first_name', 'last_name',
                'is_subscribed', 'avatar'
            )
            for field in expected_fields:
                assert field in json_data,\
                    f'В ответе должно быть поле `{field}`.'

            assert json_data['id'] == user.id, 'Неверный id.'
            assert json_data['email'] == user.email, 'Неверный email.'
            assert json_data['username'] == user.username, 'Неверный username.'
            assert json_data['first_name'] == user.first_name,\
                'Неверный first_name.'
            assert json_data['last_name'] == user.last_name,\
                'Неверный last_name.'
            assert json_data['is_subscribed'] is False,\
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
