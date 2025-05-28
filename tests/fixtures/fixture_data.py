import pytest

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart, Tag
)


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='Завтрак',
        slug='breakfast'
    )


@pytest.fixture
def another_tag():
    return Tag.objects.create(
        name='Обед',
        slug='lunch'
    )


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(
        name='Яйцо',
        measurement_unit='шт'
    )


@pytest.fixture
def another_ingredient():
    return Ingredient.objects.create(
        name='Соль',
        measurement_unit='г'
    )


@pytest.fixture
def recipe(user):
    return Recipe.objects.create(
        name='Омлет',
        text='Взбейте яйца, добавьте соль, жарьте на сковороде.',
        cooking_time=5,
        author=user
    )


@pytest.fixture
def recipe_with_ingredients_and_tags(recipe, tag, ingredient):
    recipe.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=2
    )
    return recipe


@pytest.fixture
def favorite(user, recipe):
    return Favorite.objects.create(user=user, recipe=recipe)


@pytest.fixture
def shopping_cart(user, recipe):
    return ShoppingCart.objects.create(user=user, recipe=recipe)