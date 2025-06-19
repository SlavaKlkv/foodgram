from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class AboutViewSet(ViewSet):
    def list(self, request):
        return Response(
            {'about': 'Foodgram – это сервис для публикации рецептов.'}
        )

class TechnologiesViewSet(ViewSet):
    def list(self, request):
        return Response(
            {'technologies': ['Django', 'DRF', 'PostgreSQL', 'Docker']}
        )