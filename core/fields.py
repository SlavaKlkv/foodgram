import re

from django.core.validators import MinValueValidator
from django.db import models
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError


class CustomBase64ImageField(Base64ImageField):
    default_error_messages = {
        'required': 'Обязательно поле.',
        'invalid_image': 'Неверный формат изображения.',
        'blank': 'Поле для картинки не может быть пустым.',
    }
    def to_internal_value(self, data):
        if data == '':
            raise ValidationError(self.error_messages.get('blank'))

        data_uri = r'^data:image/[A-Za-z0-9]+;base64,[A-Za-z0-9+/]+={0,2}$'

        if not re.match(data_uri, data):
            raise ValidationError(self.error_messages.get('invalid_image'))
        try:
            return super().to_internal_value(data)
        except Exception:
            raise ValidationError(self.error_messages.get('invalid_image'))

class FromOneSmallIntegerField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        validators = kwargs.pop('validators', [])
        validators.append(MinValueValidator(1))
        kwargs['validators'] = validators
        super().__init__(*args, **kwargs)