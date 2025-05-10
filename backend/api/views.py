from datetime import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotAuthenticated
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django.http import FileResponse
from django.utils import timezone
from recipes.models import (Ingredient, Recipe,
                            ShoppingCart, Favorite,
                            Subscription, User,)
from .pagination import PagesPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    UserSerializer,
    SubscribedUserSerializer,
    RecipeShortLinkSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer
)
from .filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet, описывающий работу с ингредиентами"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Метод для получения ингредиентов по имени"""
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__startswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = PagesPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        if self.action == 'short_link':
            return RecipeShortLinkSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        """Метод для автоматического указания автора рецепта"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'])
    def short_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в/из избранного"""
        recipe = self.get_object()

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в/из корзины покупок"""
        recipe = self.get_object()

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_item = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _render_shopping_cart(self, ingredient_totals, recipe_names, date):
        """Формирует текстовый отчет со списком покупок"""
        from io import BytesIO

        buffer = BytesIO()

        header = f"Список покупок на {date}\n\n"
        buffer.write(header.encode('utf-8'))

        buffer.write("Рецепты в списке покупок:\n".encode('utf-8'))
        for recipe_name, author in recipe_names.items():
            recipe_line = f"- {recipe_name} (автор: {author})\n"
            buffer.write(recipe_line.encode('utf-8'))
        buffer.write("\n".encode('utf-8'))

        buffer.write("Ингредиенты для покупки:\n".encode('utf-8'))
        for i, ((name, unit), amount) in enumerate(
                sorted(ingredient_totals.items()), 1):
            ingredient_line = f"{i}. {name} - {amount} {unit}\n"
            buffer.write(ingredient_line.encode('utf-8'))

        footer = "\nСпасибо за использование сервиса Foodgram!"
        buffer.write(footer.encode('utf-8'))

        buffer.seek(0)
        return buffer

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для загрузки текстового отчета со списком покупок"""
        ingredient_totals = {}
        recipe_names = {}

        for item in (request.user.
                     shoppingcarts.all().select_related('recipe')):
            recipe_names[item.recipe.name] = item.recipe.author.username
            for ingredient_in_recipe in item.recipe.recipe_ingredients.all():
                key = (
                    ingredient_in_recipe.ingredient.name,
                    ingredient_in_recipe.ingredient.measurement_unit
                )
                ingredient_totals[key] = (ingredient_totals.get(key, 0)
                                          + ingredient_in_recipe.amount)

        report_text = self._render_shopping_cart(
            ingredient_totals,
            recipe_names,
            timezone.now().strftime('%d.%m.%Y')
        )

        return FileResponse(
            report_text,
            content_type='text/plain',
            filename='shopping_cart.txt'
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

        if request.method == 'POST':
            data = {'user': request.user.id, 'author': author.id}
            serializer = SubscriptionSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                SubscribedUserSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Метод для вывода всех авторов, на которых подписан пользователь"""
        user = request.user
        subscriptions = user.users.all().select_related('author')

        page = self.paginate_queryset(subscriptions)

        authors = [subscription.author for subscription in page]

        serializer = SubscribedUserSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
