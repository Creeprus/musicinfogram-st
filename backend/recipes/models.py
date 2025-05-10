from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import constants


class Ingredient(models.Model):
    """
    Класс для взаимодейтсвия с ингредиентами.

    :param name (CharField): Название ингредиента
    :param measurement_unit (CharField): Единица измерения количества
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=constants.INGREDIENT_NAME_MAX_LENGTH,
        help_text='Название ингредиента'
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.INGREDIENT_MEASURE_MAX_LENGTH,
        help_text='Единица измерения количества ингредиента (г, кг, шт.)'
    )

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class User(AbstractUser):
    """
    Класс для взаимодейтсвия с данными пользователя.

    :param email (EmailField): Уникальный email пользователя
    :param username (CharField): Уникальное имя пользователя
    с валидацией символов
    :param first_name (CharField): Имя пользователя
    :param last_name (CharField): Фамилия пользователя
    :param avatar (ImageField): Аватар пользователя (опционально)
    """

    email = models.EmailField(
        unique=True,
        max_length=constants.EMAIL_MAX_LENGTH,
        verbose_name='Email',
        help_text='Уникальный email пользователя'
    )

    username = models.CharField(
        max_length=constants.USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Имя пользователя',
        help_text='Уникальное имя пользователя',
        validators=[RegexValidator(
            regex=constants.USERNAME_REGEX,
            message='Username должен содержать только буквы, '
                    'цифры и следующие символы: @ . + -'
        )]
    )

    first_name = models.CharField(
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        blank=False,
        verbose_name='Имя',
        help_text='Имя пользователя'
    )

    last_name = models.CharField(
        max_length=constants.LAST_NAME_MAX_LENGTH,
        blank=False,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Изображение профиля пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.email


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
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        help_text='Название рецепта'
    )

    text = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание процесса приготовления'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
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

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Время, необходимое для приготовления блюда',
        validators=[
            MinValueValidator(
                constants.RECIPE_MIN_COOKING_TIME,
                f'Время приготовления не может быть менее '
                f'{constants.RECIPE_MIN_COOKING_TIME} '
                'минуты'
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

    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента в рецепте',
        validators=[MinValueValidator(
            constants.INGREDIENT_IN_RECIPE_MIN_AMOUNT,
            f'Количество ингредиента должно быть больше'
            f'{constants.INGREDIENT_IN_RECIPE_MIN_AMOUNT}!'
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


class UserOfRecipeBase(models.Model):
    """
    Абстрактный класс для взаимодействия пользователей с рецептами.

    :param user (ForeignKey): Пользователь, взаимодействующий с рецептом
    :param recipe (ForeignKey): Рецепт, с которым взаимодействует пользователь
    :param created_at (DateTimeField): Дата создания записи
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss',
        help_text='Пользователь, взаимодействующий с рецептом'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)ss',
        help_text='Рецепт, с которым взаимодействует пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время добавления записи'
    )

    class Meta:
        """Meta класс описания объекта"""
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(UserOfRecipeBase):
    """
    Класс модели избранных рецептов.
    """

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['created_at']


class ShoppingCart(UserOfRecipeBase):
    """
    Класс модели корзины покупок.
    """

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        ordering = ['created_at']


class Subscription(models.Model):
    """
    Класс, описывающий взаимодействие с подписками пользователей на рецепты.

    :param user (ForeignKey): Пользователь, который подписывается
    :param author (ForeignKey): Автор рецептов, на которого подписываются
    :param created_at (DateTimeField): Дата создания подписки
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Пользователь',
        help_text='Пользователь, который подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор рецептов',
        help_text='Автор рецептов, на которого подписываются'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время создания подписки'
    )

    class Meta:
        """Meta класс описания объекта"""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
