import pytest
from rest_framework.test import APIClient



@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(
        username='testuser', email='testuser@email.com', password='1234567'
    )
    user.plaintext_password = '1234567'
    return user


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(
        username='testuser2', email='testuser2@email.com', password='1234567'
    )


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create_user(
        username='testuseranother', email='testuseranother@email.com', password='1234567'
    )


@pytest.fixture
def token_user(user):
    client = APIClient()
    response = client.post('/api/auth/token/login/', {
        'email': 'testuser@email.com',
        'password': '1234567'
    })
    token = response.data.get('auth_token')
    return token

@pytest.fixture
def auth_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user}')
    return client
