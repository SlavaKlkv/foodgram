import pytest

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from tests.test_utils import generate_base64_image


@pytest.fixture
def tag():
    return Tag.objects.create(name="Завтрак", slug="breakfast")


@pytest.fixture
def tag_2():
    return Tag.objects.create(name="Обед", slug="lunch")


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(name="Яйцо", measurement_unit="шт")


@pytest.fixture
def ingredient_2():
    return Ingredient.objects.create(name="Соль", measurement_unit="г")


@pytest.fixture
def ingredient_3():
    return Ingredient.objects.create(name="Картофель", measurement_unit="г")


@pytest.fixture
def ingredient_4():
    return Ingredient.objects.create(name="Молоко", measurement_unit="мл")


@pytest.fixture
def recipe(user):
    return Recipe.objects.create(
        name="Омлет",
        text="Взбейте яйца, добавьте соль, жарьте на сковороде.",
        cooking_time=5,
        author=user,
        image=generate_base64_image(),
    )


@pytest.fixture
def recipe_2(user_2):
    return Recipe.objects.create(
        name="Картофельное пюре с молоком",
        text="Отварите картофель, разомните и добавьте молоко.",
        cooking_time=10,
        author=user_2,
        image=generate_base64_image(),
    )


@pytest.fixture
def recipe_with_ingredients_and_tags(recipe, tag, ingredient, ingredient_2):
    recipe.tags.add(tag)
    for ing, amount in ((ingredient, 2), (ingredient_2, 5)):
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ing, amount=amount)
    return recipe


@pytest.fixture
def recipe_with_ingredients_and_tags_2(
        recipe_2, tag_2, ingredient_3, ingredient_4):
    recipe_2.tags.add(tag_2)
    for ing, amount in ((ingredient_3, 150), (ingredient_4, 40)):
        RecipeIngredient.objects.create(
            recipe=recipe_2, ingredient=ing, amount=amount)
    return recipe_2


@pytest.fixture
def favorite(user, recipe):
    return Favorite.objects.create(user=user, recipe=recipe)


@pytest.fixture
def shopping_cart(user, recipe):
    return ShoppingCart.objects.create(user=user, recipe=recipe)
