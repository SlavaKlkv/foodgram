import base64
import io
from http import HTTPStatus

from PIL import Image


def list_available(url, fixture_name):
    """Список доступен определенным пользователям."""

    response = getattr(fixture_name, 'get')(url)

    assert response.status_code == HTTPStatus.OK, (
        f'GET {url} должен возвращать 200, '
        f'но вернул {response.status_code}'
    )
    assert 'results' in response.json(), (
        f'Ответ {url} должен содержать ключ "results"'
    )
    assert isinstance(response.json().get('results'), list), (
        f'Значение ключа "results" из {url} должно быть списком'
    )

def generate_base64_image(color='blue', size=(100, 100), fmt='PNG'):
    """Генерирует base64-строку изображения заданного цвета и размера."""
    image = Image.new('RGB', size, color=color)
    buffered = io.BytesIO()
    image.save(buffered, format=fmt)
    return (
        'data:image/png;base64,' +
        base64.b64encode(buffered.getvalue()).decode('utf-8')
    )