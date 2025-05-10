from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, ReadOnlyField

from recipes.models import (
    Favorite, Recipe, ShoppingCart,
    IngredientInRecipe, Ingredient,
    Subscription, User)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Meta класс описания объекта"""
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сераилазатор для ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        """Meta класс описания объекта"""
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для получения пользователей с дополнительными полями."""

    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(required=False)

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
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                author=user,
                user=request.user
            ).exists()
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        """Meta класс описания объекта"""
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'author',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def _check_existence(self, model, recipe):
        """Функция для проверки существования рецепта для
         авторизированного пользователя."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()
        )

    def get_is_favorited(self, recipe):
        """Функция для получения информации, если рецепт избранный."""
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        """Функция для получения информации, если рецепт в корзине."""
        return self._check_existence(ShoppingCart, recipe)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        """Meta класс описания объекта"""
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'cooking_time',
            'ingredients',
        )

    def validate(self, data):
        """Функция валидации данных рецепта."""

        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients обязательно для заполнения'
            })

        ingredients_data = data.get('recipe_ingredients', [])
        if not ingredients_data:
            raise serializers.ValidationError({
                'ingredients': 'Список ингредиентов не может быть пустым'
            })

        ingredient_ids = [
            item['ingredient']['id'].id for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты в рецепте не должны повторяться'
            })

        if 'image' not in data:
            raise serializers.ValidationError({
                'image': 'Поле image не может быть пустым'
            })

        return data

    def create(self, validated_data):
        """Функция для создания рецепта."""

        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Функция для обновления рецепта."""

        if 'recipe_ingredients' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredients')
            instance.ingredients.clear()
            self._save_ingredients(instance, ingredients_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def _save_ingredients(self, recipe, ingredients_data):
        """Функция для создания ингредиентов."""

        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        )

    def to_representation(self, instance):
        """Представление после создания/обновления рецепта."""

        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class RecipeShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта в подписках."""

    class Meta:
        """Meta класс описания объекта"""
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribedUserSerializer(UserSerializer):
    """Сериалазатор для получения информации об авторах,
    на которых подписан текущий пользователь"""

    recipes = SerializerMethodField()
    recipes_count = ReadOnlyField(source='recipes.count')

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
        """Функция для получения рецептов автора."""

        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')

        recipes = author.recipes.all()

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return RecipeShortLinkSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Авторизация обязательна')

        return data

    def to_representation(self, instance):
        return RecipeShortLinkSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Авторизация обязательна')

        return data

    def to_representation(self, instance):
        return RecipeShortLinkSerializer(
            instance.recipe,
            context=self.context
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Авторизация обязательна')

        if data['user'] == data['author']:
            raise serializers.ValidationError('Нельзя'
                                              ' подписаться на самого себя')

        return data
