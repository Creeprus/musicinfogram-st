from django.contrib import admin
from app.models import IngredientInRecipe


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Класс, для справочной сущности IngredientRecipe (админ)."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
