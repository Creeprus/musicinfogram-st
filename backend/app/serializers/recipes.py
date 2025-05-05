from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from ..models import Favorite, Recipe, ShoppingCart, IngredientInRecipe
from .ingredients import IngredientInRecipeSerializer


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецепта."""

    class Meta:
        """Meta класс описания объекта"""
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = serializers.SerializerMethodField()
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, required=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

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

    def validate_image(self, value):
        """Функция для валидации изображения."""
        if not value:
            raise serializers.ValidationError(
                "Поле image не может быть пустым"
            )
        return value

    def validate_ingredients(self, value):
        """Функция для валидации ингредиента."""
        if not value:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым"
            )
        ingredient_ids = [item['ingredient']['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты в рецепте не должны повторяться"
            )

        return value

    def validate(self, data):
        """Функция для валидации ингредиента (пустой?)."""
        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients обязательно для заполнения'
            })
        return data

    def get_author(self, obj):
        """Функция для получения автора."""
        from .users import UserSerializer
        return UserSerializer(obj.author, context=self.context).data

    def create(self, validated_data):
        """Функция для создания рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Функция для обновления ингредиента."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        """Функция для создания ингредиента."""
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        )

    def _check_existence(self, model, recipe):
        """Функция для проверки существования рецепта для
         авторизированного пользователя."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
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


class RecipeShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для получения короткой ссылки на рецепт."""

    short_link = serializers.SerializerMethodField(
        method_name='get_short_link')

    class Meta:
        """Meta класс описания объекта"""
        model = Recipe
        fields = ('short_link',)

    def get_short_link(self, obj):
        """Функция для получения короткой ссылки."""
        request = self.context.get('request')
        return request.build_absolute_uri(f'/recipes/{obj.id}/')

    def to_representation(self, instance):
        """Функция для репрезентации короткой ссылки."""
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}
