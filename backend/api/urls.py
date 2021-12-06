from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (IngredientsView, NewObtainAuthToken, RecipeView, TagsView,
                    UserView)

router = DefaultRouter()
router.register('users', UserView, basename='user')
router.register('recipes', RecipeView, basename='recipe')
router.register('ingredients', IngredientsView, basename='ingredients')
router.register('tags', TagsView, basename='tags')


urlpatterns = [
    path('auth/token/login/', NewObtainAuthToken.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('', include(router.urls)),
]
