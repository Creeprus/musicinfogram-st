from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Subscription, User


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Функция для создания пользователя."""
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для получения пользователей с дополнительными полями."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def get_is_subscribed(self, user):
        """Функция для получения информации о подписках пользователя."""
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=user.id,
            user=request_user.id
        ).exists()


class SubscribedUserSerializer(UserSerializer):
    """Сериалазатор для получения информации об авторах,
    на которых подписан текущий пользователь"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        """Meta класс описания объекта"""
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, author):
        """Функция для получения рецепта автора."""
        from .recipes import ShortRecipeSerializer
        recipes_limit = int(self.context.get('request')
                            .GET.get('recipes_limit', 3))
        recipes = author.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, author):
        """Функция для получения количества рецептов."""
        return author.recipes.count()

    def to_representation(self, instance):
        """Функция для получения короткой ссылки."""
        data = super().to_representation(instance)
        required_fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        ]
        for field in required_fields:
            if field not in data:
                data[field] = None
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа при создании подписки."""
    user = serializers.StringRelatedField()
    author = serializers.StringRelatedField()

    class Meta:
        """Meta класс описания объекта"""
        model = Subscription
        fields = ('user', 'author')
