NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
TAG_FIELD_MAX_LENGTH = 32
MEASUREMENT_UNIT_MAX_LENGTH = 64
INGREDIENT_TITLE_MAX_LENGTH = 128
RECIPE_TITLE_MAX_LENGTH = 256
NON_EXISTENT_ID = 1000000

UNAUTH_AND_AUTH_CLIENTS = ("client", "auth_client")

# Users
USERS_URL = "/api/users/"
USER_DETAIL_URL = "/api/users/{id}/"
USER_ME_URL = "/api/users/me/"
USER_AVATAR_URL = "/api/users/me/avatar/"
USER_PASSWORD_URL = "/api/users/set_password/"
USER_LOGIN_URL = "/api/auth/token/login/"
USER_LOGOUT_URL = "/api/auth/token/logout/"
USER_SUBSCRIBE_URL = "/api/users/{id}/subscribe/"
USER_SUBSCRIPTIONS_URL = "/api/users/subscriptions/"

# Tags
TAGS_URL = "/api/tags/"
TAG_DETAIL_URL = "/api/tags/{id}/"

# Ingredients
INGREDIENTS_URL = "/api/ingredients/"
INGREDIENT_DETAIL_URL = "/api/ingredients/{id}/"

# Recipes
RECIPES_URL = "/api/recipes/"
RECIPE_DETAIL_URL = "/api/recipes/{id}/"
RECIPE_DOWNLOAD_SHOPPING_CART_URL = "/api/recipes/download_shopping_cart/"
RECIPE_SHOPPING_CART_URL = "/api/recipes/{id}/shopping_cart/"
RECIPE_FAVORITE_URL = "/api/recipes/{id}/favorite/"
RECIPE_GET_LINK_URL = "/api/recipes/{id}/get-link/"
