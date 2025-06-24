from core.constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH
from core.managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name="Адрес электронной почты"
    )
    username = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя пользователя",
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="users/",
        blank=False,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followings",
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = 'объект "Подписка"'
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            )
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"
