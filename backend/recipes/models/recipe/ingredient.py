from django.db import models


class Ingredient(models.Model):
    """
    Класс для взаимодейтсвия с ингредиентами.

    :param name (CharField): Название ингредиента
    :param measurement_unit (CharField): Единица измерения количества
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=128,
        help_text='Название ингредиента'
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=64,
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
