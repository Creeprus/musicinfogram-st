from django.db import models
from ..user.user import User
from ..recipe.recipe import Recipe


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


class ShoppingCart(UserOfRecipeBase):
    """
    Класс модели корзины покупок.
    """

    class Meta:
        """Meta класс описания объекта"""
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
