from recipes.models import Recipe


def generate_shopping_list(user):
    recipes = Recipe.objects.filter(
        is_in_shopping_cart__user=user).prefetch_related(
        'recipe_ingredients__ingredient'
    )

    ingredients = {}
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            key = (
                recipe_ingredient.ingredient.name,
                recipe_ingredient.ingredient.measurement_unit,
            )
            ingredients[key] = (
                ingredients.get(key, 0) + recipe_ingredient.amount
            )

    lines = ["Список покупок:"]
    for (name, unit), amount in ingredients.items():
        lines.append(f"- {name} ({unit}) — {amount}")
    return "\n".join(lines)
