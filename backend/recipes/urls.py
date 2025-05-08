from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
)
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
