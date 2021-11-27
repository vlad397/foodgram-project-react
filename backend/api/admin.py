from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tags)

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    search_fields = ('email', 'username',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_filter = ('author', 'name', 'tags')

    def in_favorite(self, obj):
        return Favorite.objects.filter(recipes=obj).count()

    def get_fields(self, request, obj=None):
        if obj is not None:
            return self.fields
        else:
            fields = list(self.fields)
            fields.remove('in_favorite')
            return fields

    list_display = ('name', 'author', 'in_favorite')
    readonly_fields = ('in_favorite',)
    fields = ('in_favorite', 'author', 'name',
              'image', 'text', 'tags', 'cooking_time')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tags)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
