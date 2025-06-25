from rest_framework import serializers

from core.exceptions import ValidationError
from core.fields import CustomBase64ImageField
from users.serializers import UserProfileSerializer

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class BaseRecipeSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class RecipeReadSerializer(BaseRecipeSerializer):
    pass


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, write_only=True)


class RecipeWriteSerializer(BaseRecipeSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = CustomBase64ImageField()

    class Meta(BaseRecipeSerializer.Meta):
        model = Recipe
        fields = BaseRecipeSerializer.Meta.fields

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def validate_ingredients(self, value):
        value = self._validate_nonempty(
            value, "ингредиент", field_name="ingredients")
        request = self.context.get("request")
        if request and request.method == "PATCH":
            errors = self._collect_patch_errors(value)
            if errors:
                raise ValidationError({"ingredients": errors})
        return value

    def _collect_patch_errors(self, ingredients):
        errors = []
        for ingredient in ingredients:
            error_dict = self._check_patch_ingredient(ingredient)
            errors.append(error_dict if error_dict else None)
        return [e for e in errors if e]

    def validate_tags(self, value):
        return self._validate_nonempty(value, "тег", field_name="tags")

    def validate(self, data):
        request = self.context.get("request")
        if request and request.method == "PATCH":
            required_fields = ("ingredients", "tags",
                               "name", "text", "cooking_time")
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise ValidationError(
                    {field: ["Обязательное поле."] for field in missing}
                )
        ingredients = data.get("ingredients")
        if ingredients is not None:
            self._validate_unique_ids(
                items=ingredients,
                field_name="ingredients",
                object_name="Ингредиенты",
                lookup=lambda ingredient_obj: ingredient_obj.get("id").id,
            )
        tags = data.get("tags")
        if tags is not None:
            self._validate_unique_ids(
                items=tags,
                field_name="tags",
                object_name="Теги",
                lookup=lambda tag: tag.id,
            )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        request = self.context.get("request")
        author = request.user if request else None

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)

        for item in ingredients_data:
            recipe.ingredients.add(
                item.get("id"), through_defaults={"amount": item.get("amount")}
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.ingredients.clear()
            for item in ingredients_data:
                instance.ingredients.add(
                    item.get("id"), through_defaults={
                        "amount": item.get("amount")})

        return instance

    @staticmethod
    def _validate_nonempty(value, object_name, field_name):
        if not value:
            raise ValidationError(
                {field_name: f"Должен быть хотя бы один {object_name}."}
            )
        return value

    @staticmethod
    def _validate_unique_ids(*, items, field_name, object_name, lookup):
        ids = tuple(lookup(item) for item in items)
        if len(ids) != len(set(ids)):
            raise ValidationError(
                {field_name: f"{object_name} должны быть уникальны."})

    @staticmethod
    def _check_patch_ingredient(ingredient):
        error_dict = {}
        error_message = "Обязательное поле."
        if "id" not in ingredient:
            error_dict["id"] = [error_message]
        if "amount" not in ingredient:
            error_dict["amount"] = [error_message]
        return error_dict
