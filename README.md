# Foodgram

## Описание

Кратко: Foodgram — это сервис публикации и поиска кулинарных рецептов  
с возможностью добавления их в избранное,  
подписки на авторов и создания списка покупок.

---

## Установка

### Как развернуть проект на локальной машине

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/SlavaKlkv/foodgram.git
    cd foodgram
    ```

2. Создайте и заполните `.env` (см. пример ниже).

3. Соберите и запустите контейнеры:
    ```bash
    docker compose -f infra/docker-compose.yml up -d --build
    ```

---

## Примеры API-запросов

### Пример: получить список рецептов

**GET** `/api/recipes/`

Ответ:
```json
[
  {
    "id": 0,
    "tags": [
      {
        "id": 0,
        "name": "Завтрак",
        "slug": "breakfast"
      }
    ],
    "author": {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": false,
      "avatar": "http://foodgram.example.com/media/avatars/avatar.png"
    },
    "ingredients": [
      {
        "id": 0,
        "name": "Картофель отварной",
        "measurement_unit": "г",
        "amount": 1
      }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": false,
    "name": "Омлет",
    "image": "http://fdgrm.duckdns.org/media/recipes/images/image.png",
    "text": "Взбейте яйца, добавьте молоко, обжарьте.",
    "cooking_time": 10
  }
]
```

---

### Пример: создать рецепт

**POST** `/api/recipes/`

Тело запроса:
```json
{
  "ingredients": [
    {"id": 1, "amount": 100},
    {"id": 2, "amount": 200}
  ],
  "tags": [1, 2],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "name": "Омлет",
  "text": "Взбейте яйца, добавьте молоко, обжарьте.",
  "cooking_time": 10
}
```

Ответ:
```json
{
  "id": 2,
  "author": { ... },
  "ingredients": [ ... ],
  "is_favorited": true,
  "..."
}
```

## Пример содержимого `.env`-файла

```
USE_SQLITE=1
DEBUG=True

SECRET_KEY='secret_key'

POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=posgress_password
POSTGRES_DB=db_name

# Переменные для Django-проекта:
DB_HOST=host_name
DB_PORT=3957

COMPOSE_BAKE=true

```

---

## Запуск миграций

```bash
sudo docker compose -f infra/docker-compose.production.yml exec backend python manage.py migrate
```

---

## Запуск приложения

```bash
sudo docker compose -f infra/docker-compose.production.yml up -d
```

---

## Импорт данных из файла

```bash
sudo docker compose -f infra/docker-compose.production.yml exec backend python manage.py import_ingredients
```

---

## Адрес, где развернут проект и данные для входа в админку

- http://fdgrm.duckdns.org  
- Админка: http://fdgrm.duckdns.org/admin  
  - Логин: `superuser@email.com`
  - Пароль: `superuserpassword`