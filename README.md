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
    ```
   Перейдите в корень проекта:
   ```bash
    cd foodgram
   ```

2. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    ```
    Для Linux/macOS
    ```bash
    source venv/bin/activate
    ```
    Для Windows:
    ```bash
    venv\Scripts\activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r backend/requirements.txt
    ```

4. Создайте и заполните `.env`(пример ниже).

    ```
    USE_SQLITE=1
    DEBUG=True
    CSRF_TRUSTED_ORIGINS=https://site-domen.com
    
    SECRET_KEY='secret_key'
    
    POSTGRES_USER=postgres_user
    POSTGRES_PASSWORD=posgress_password
    POSTGRES_DB=db_name
    
    # Переменные для Django-проекта:
    DB_HOST=host_name
    DB_PORT=3957

    COMPOSE_BAKE=true
    ```
    
## Запуск миграций

```bash
  python backend/manage.py migrate
```
     
## Запуск приложения
    
```bash
  docker compose -f infra/docker-compose.yml up -d --build
```
    
    
## Импорт данных из файла
    
```bash
  python backend/manage.py import_ingredients backend/data/ingredients.csv
```
    
    
## Примеры API-запросов
    
### Пример: получить список рецептов
    
**GET** `/api/recipes/`

Ответ:
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
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
        "avatar": "http://foodgram.example.org/media/users/image.png"
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
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

---

### Пример: создать рецепт
    
**POST** `/api/recipes/`

Тело запроса:
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Ответ:
```json
{
  "id": 0,
  "tags": [...],
  "author": {...},
  "ingredients": [...],
  "is_favorited": true,
  "is_in_shopping_cart": false,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
    
## Адрес, где развернут проект и данные для входа в админку
    
- http://fdgrm.duckdns.org  
- Админка: http://fdgrm.duckdns.org/admin  
  - Логин: `superuser@email.com`
  - Пароль: `superuserpassword`