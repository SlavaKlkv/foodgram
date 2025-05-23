from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ValidationError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ошибка валидации.'
    default_code = 'validation_error'

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    print('>>> exc:', type(exc), exc)
    print('>>> response:', response)

    if response is None:
        response = Response(
            {'detail': 'Произошла неизвестная ошибка.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, ValidationError):
        response = Response(
            {'detail': exc.detail},
            status=exc.status_code
        )
    elif isinstance(exc, IntegrityError):
        response = Response(
            {'detail': 'Вы уже подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return response
