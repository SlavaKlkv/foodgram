from django.http import Http404
from rest_framework.exceptions import NotFound


class CustomGetObjectMixin:
    object = 'объекта'

    @property
    def not_found_detail(self):
        return f'Такого {self.object} не существует.'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail=self.not_found_detail)