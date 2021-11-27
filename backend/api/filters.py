from django_filters.filters import CharFilter, ChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from .models import Recipe

choices = ((0, 0), (1, 1))


class CustomFilter(FilterSet):
    author = NumberFilter(field_name='author')
    tags = CharFilter(field_name='tags__slug', lookup_expr='iexact')
    is_favorited = ChoiceFilter(method='filter_is_favorited', choices=choices)
    is_in_shopping_cart = ChoiceFilter(
        method='filter_is_in_shopping_cart', choices=choices
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                recipes = Recipe.objects.filter(favorite_recipes__user=user)
                return queryset & recipes
            elif value == '0':
                recipes = Recipe.objects.exclude(favorite_recipes__user=user)
                return queryset & recipes
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                recipes = Recipe.objects.filter(cart_recipes__user=user)
                return queryset & recipes
            elif value == '0':
                recipes = Recipe.objects.exclude(cart_recipes__user=user)
                return queryset & recipes
        else:
            return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']
