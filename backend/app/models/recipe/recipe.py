from django.core.validators import MinValueValidator
from django.db import models
from ..user.user import User
from .ingredient import Ingredient


class Recipe(models.Model):
    """
    Класс  для взаимодействия с рецептам пользователей.

    :param name (CharField): Название рецепта
    :param text (TextField): Подробное описание процесса приготовления
    :param ingredients (ManyToManyField):
    :param Связь с ингредиентами через промежуточную модель
    :param image (ImageField): Изображение готового блюда
    :param author (ForeignKey): Создатель рецепта
    :param cooking_time (IntegerField): Время приготовления в минутах
    :param created_at (DateTimeField): Дата и время создания рецепта
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        help_text='Название рецепта'
    )

    text = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание процесса приготовления'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text='Список необходимых ингредиентов'
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        help_text='Изображение готового блюда'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Создатель рецепта'
    )

    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Время, необходимое для приготовления блюда',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть менее 1 минуты'
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время публикации рецепта'
    )

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'ID рецепта: {self.id} | {self.name}'


class IngredientInRecipe(models.Model):
    """
    Класс для взаимодействия с ингредиентами в рецептах.

    :param recipe (ForeignKey): Связанный рецепт
    :param ingredient (ForeignKey): Используемый ингредиент
    :param amount (IntegerField): Количество ингредиента
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт, в котором используется ингредиент'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Используемый ингредиент'
    )

    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента в рецепте',
        validators=[MinValueValidator(
            1,
            'Количество ингредиента должно быть больше нуля!'
        )]
    )

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Продукт рецепта'
        verbose_name_plural = 'Продукты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'
