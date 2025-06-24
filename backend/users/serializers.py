from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.constants import DIGITS
from core.exceptions import ValidationError
from core.fields import CustomBase64ImageField
from logging_setup import logger_setup
from users.models import Subscription

logger = logger_setup()

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name")


class UserCreateSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ("password",)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserProfileSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(use_url=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ("is_subscribed", "avatar")

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.followers.filter(author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = CustomBase64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class SubscriptionSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True, use_url=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    class Meta(UserProfileSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + (
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
            "author",
        )
        extra_kwargs = {
            "email": {"read_only": True},
            "username": {"read_only": True},
            "first_name": {"read_only": True},
            "last_name": {"read_only": True},
        }

    def to_representation(self, instance):
        return super().to_representation(instance.author)

    def get_recipes(self, obj):
        # Чтобы избежать циклического импорта
        from recipes.serializers import RecipeShortSerializer

        recipes_limit = self.context.get(
            "request").query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit is not None and recipes_limit in str(DIGITS):
            recipes = recipes[: int(recipes_limit)]

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, attrs):
        if self.context["request"].user == attrs["author"]:
            raise ValidationError("Нельзя подписаться на самого себя.")
        return attrs

    def validate_author(self, author):
        user = self.context["request"].user
        request = self.context["request"]
        is_subscribed = Subscription.objects.filter(
            user_id=user.id, author_id=author.id
        ).exists()
        if request.method == "POST" and is_subscribed:
            raise ValidationError("Вы уже подписаны на этого пользователя.")
        if request.method == "DELETE" and not is_subscribed:
            raise ValidationError("Подписка не найдена.")
        return author

    def create(self, validated_data):
        author = validated_data["author"]
        user = self.context["request"].user
        return Subscription.objects.create(user=user, author=author)
