from http import HTTPStatus

import pytest

from core.constants import USER_SUBSCRIBE_URL, USER_SUBSCRIPTIONS_URL
from users.models import Subscription

from .test_utils import list_available


@pytest.mark.django_db(transaction=True)
class TestSubscriptions:

    def test_get_subscriptions_returns_200(self, auth_client):
        """Получение списка подписок возвращает 200."""
        list_available(USER_SUBSCRIPTIONS_URL, auth_client)

    def test_subscribe_successfully_creates_subscription(
            self, auth_client, user_2):
        """Успешная подписка создаёт объект подписки."""

        url = USER_SUBSCRIBE_URL.format(id=user_2.id)
        subscriptions_before = Subscription.objects.count()
        response = auth_client.post(url)

        assert response.status_code == HTTPStatus.CREATED, (
            f"POST {url} должен возвращать 201, "
            f"но вернул {response.status_code}"
        )
        assert (
            Subscription.objects.count() == subscriptions_before + 1
        ), "Количество подписок должно увеличиться на 1."

    @pytest.mark.parametrize(
        "target_id, error_text",
        [
            pytest.param("self", "Нельзя подписаться на самого себя."),
            pytest.param(
                "duplicate", "Вы уже подписаны на этого пользователя."),
        ],
    )
    def test_user_cannot_subscribe_invalid_cases(
        self, auth_client, user, user_2, target_id, error_text
    ):
        """Попытки подписаться на себя и повторно возвращают 400."""
        url = USER_SUBSCRIBE_URL.format(
            id=user.id if target_id == "self" else user_2.id
        )
        if target_id == "duplicate":
            Subscription.objects.create(user=user, author=user_2)

        subscriptions_before = Subscription.objects.count()
        response = auth_client.post(url)
        subscriptions_after = Subscription.objects.count()

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"POST {url} должен возвращать 400, "
            f"но вернул {response.status_code}"
        )
        assert (
            subscriptions_after == subscriptions_before
        ), "Количество подписок не должно измениться при ошибке."
        assert error_text in response.json().get("detail", ""), (
            f"Ожидалось сообщение об ошибке: '{error_text}', "
            f"но было: {response.json()}"
        )

    def test_unsubscribe_successfully_deletes_subscription(
        self, auth_client, user, user_2
    ):
        """Успешная отписка удаляет объект подписки."""
        Subscription.objects.create(user=user, author=user_2)
        url = USER_SUBSCRIBE_URL.format(id=user_2.id)
        subscriptions_before = Subscription.objects.count()
        response = auth_client.delete(url)
        subscriptions_after = Subscription.objects.count()

        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f"DELETE {url} должен возвращать 204, "
            f"но вернул {response.status_code}"
        )
        assert (
            subscriptions_after == subscriptions_before - 1
        ), "Количество подписок должно уменьшиться на 1."
