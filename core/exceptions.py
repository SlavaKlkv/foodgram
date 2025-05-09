from rest_framework import status


class ValidationError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ('Ошибка валидации.')
    default_code = 'validation_error'

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)
