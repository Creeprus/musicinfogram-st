from rest_framework import viewsets

from ..models import Ingredient
from ..serializers import IngredientSerializer


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
