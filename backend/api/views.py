from rest_framework import viewsets

from recipes.models import Ingredient
from api.serializers import IngredientSerializer
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotAuthenticated
from recipes.models import Favorite, Recipe, ShoppingCart
from .pagination import PagesPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeSerializer,
    ShortRecipeSerializer,
    RecipeShortLinkSerializer
)
from recipes.models import Subscription, User
from .pagination import PagesPagination
from .serializers import (
    UserSerializer,
    SubscribedUserSerializer,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)


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
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = PagesPagination

    def get_queryset(self):
        """Метод для получения рецептов"""
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        if is_favorited == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)
        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(
                shoppingcarts__user=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        """Метод для автоматического указания автора рецепта"""
        serializer.save(author=self.request.user)

    @staticmethod
    def _toggle_favorite_or_shopping_cart(request, recipe, model):
        """Метод для создания и удаления рецептов
          в списке избранных или в корзине покупок"""
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe,
            )
            if not created:
                raise ValidationError({'errors': 'Рецепт уже добавлен'})

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        try:
            instance = model.objects.get(
                user=request.user,
                recipe=recipe
            )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            raise ValidationError(
                {'errors': 'Рецепт не найден в списке'},
                code=status.HTTP_400_BAD_REQUEST
            ) from None

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def change_favorited_recipes(self, request, pk=None):
        """Метод для добавления или удаления рецепта из избранного"""
        return self._toggle_favorite_or_shopping_cart(
            request,
            get_object_or_404(Recipe, pk=pk),
            Favorite
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart'
    )
    def change_shopping_cart(self, request, pk=None):
        """Метод для добавления или удаления рецепта из списка покупок"""
        return self._toggle_favorite_or_shopping_cart(
            request,
            get_object_or_404(Recipe, pk=pk),
            ShoppingCart
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart'
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

    def _render_shopping_cart(self, ingredient_totals, recipe_names, date):
        """Метод для формирования текста списка покупок"""
        report_lines = [
            f'Список покупок на {date}:',
            'Продукты:',
        ]

        for number_of_product, ((name, unit), amount) in enumerate(
            sorted(ingredient_totals.items(), key=lambda x: x[0]),
            start=1
        ):
            report_lines.append(
                f'{number_of_product}. '
                f'{name.capitalize()} ({unit}) - {amount}'
            )

        report_lines.append('\nРецепты, для которых нужны эти продукты:')
        for number_of_product, (recipe_name, author) in enumerate(
            sorted(recipe_names.items()),
            start=1
        ):
            report_lines.append(
                f'{number_of_product}. {recipe_name} (автор: {author})'
            )

        return '\n'.join(report_lines)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт"""
        recipe = self.get_object()
        serializer = RecipeShortLinkSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


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
