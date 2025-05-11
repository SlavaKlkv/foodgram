from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError


class CustomBase64ImageField(Base64ImageField):
    def to_internal_value(self, data):
        if data == '':
            raise ValidationError(
                'Поле для картинки не может быть пустым.')
        return super().to_internal_value(data)
