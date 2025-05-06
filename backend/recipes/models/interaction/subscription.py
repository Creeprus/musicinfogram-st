from django.db import models
from ..user.user import User


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

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
