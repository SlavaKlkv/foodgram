from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription, User
from users.serializers import (AvatarSerializer, PasswordSerializer,
                               SubscriptionSerializer)


class UserViewSet(DjoserUserViewSet):

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        if self.action in ('subscribe', 'unsubscribe'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all()

    def _handle_subscription(self, request, action):
        user = request.user
        author = self.get_object()

        if action == 'create':
            subscription = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(subscription, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if action == 'delete':
            Subscription.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id=None):
        return self._handle_subscription(request, 'create')

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        return self._handle_subscription(request, 'delete')

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user_subscriptions = Subscription.objects.filter(user=request.user)
        pages = self.paginate_queryset(user_subscriptions)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['put'], url_path='me/avatar')
    def set_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(
            user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @set_avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(current_password):
            return Response(
                {'current_password': ['Неверный текущий пароль.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Пароль успешно изменён.'}, status=status.HTTP_204_NO_CONTENT)
