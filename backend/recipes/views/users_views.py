from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotAuthenticated

from recipes.models import Subscription, User
from recipes.pagination import PagesPagination
from recipes.serializers import (
    UserSerializer,
    SubscribedUserSerializer,
)


class UserViewSet(DjoserUserViewSet):
    """ViewSet, описывающий работу с пользователями и подписками"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagesPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """Переопределение разрешений для метода me"""
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        url_path='me'
    )
    def get_me(self, request):
        """Метод для получения текущего пользователя"""
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def change_avatar(self, request):
        """Метод для смены или удаления аватара пользователя"""
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                raise ValidationError(
                    {'avatar': ['Это поле обязательно.']}
                )
            serializer = self.get_serializer(
                user, data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )
        user.avatar.delete()
        user.save()
        return Response(
            {'message': 'Аватар успешно удалён'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe'
    )
    def subscribe_and_unsubscribe(self, request, id=None):
        """Метод для создания и удаления подписки на авторов"""
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            raise ValidationError(
                {'error': 'Нельзя подписаться на самого себя'}
            )

        if request.method == 'POST':
            _, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )

            if not created:
                raise ValidationError(
                    {'errors': 'Подписка уже была оформлена'}
                )

            return Response(
                SubscribedUserSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        try:
            subscription = Subscription.objects.get(
                user=request.user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            raise ValidationError(
                {'error': 'Подписка не найдена'},
                code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Метод для вывода всех авторов, на которых подписан пользователь"""
        user = request.user
        subscriptions = (
            user.users.all()
            .select_related('author')
        )

        paginator = PagesPagination()
        paginator.page_size = request.query_params.get('limit', 6)
        paginated_subscriptions = paginator.paginate_queryset(
            subscriptions,
            request
        )

        authors = [
            subscription.author for subscription in paginated_subscriptions
        ]

        serializer = SubscribedUserSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
