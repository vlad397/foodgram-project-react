from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsView, Logout, NewObtainAuthToken, RecipeView,
                    TagsView, UserView)

router = DefaultRouter()
router.register('users', UserView, basename='user')
router.register('recipes', RecipeView, basename='recipe')
router.register('ingredients', IngredientsView, basename='ingredients')
router.register('tags', TagsView, basename='tags')


urlpatterns = [
    path('auth/token/login/', NewObtainAuthToken.as_view()),
    path('auth/token/logout/', Logout.as_view()),
    path('', include(router.urls)),
]
