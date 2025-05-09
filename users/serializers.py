from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from core.constants import DIGITS
from core.exceptions import ValidationError

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserCreateSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('password',)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(use_url=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('is_subscribed', 'avatar')  # type: ignore

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class SubscriptionSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ('recipes', 'recipes_count')

    def to_representation(self, instance):
        return super().to_representation(instance.author)

    def get_recipes(self, obj):
        from recipes.serializers import RecipeShortSerializer  # Чтобы избежать циклического импорта
        recipes_limit = self.context.get('request').query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None and recipes_limit in DIGITS:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, attrs):
        if self.context['request'].user == attrs['author']:
            raise ValidationError('Нельзя подписаться на самого себя.')
        return attrs

    def validate_author(self, author):
        user = self.context['request'].user
        request = self.context['request']
        is_subscribed = user.follower.filter(author=author).exists()
        if request.method == 'POST' and is_subscribed:
            raise ValidationError('Вы уже подписаны на этого пользователя.')
        if request.method == 'DELETE' and not is_subscribed:
            raise ValidationError('Подписка не найдена.')
        return author
