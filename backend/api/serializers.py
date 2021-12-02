from collections import OrderedDict

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


class NewAuthTokenSerializer(serializers.Serializer):
    '''Сериализатор получения токена'''
    email = serializers.EmailField(
        label=('Email'),
        write_only=True
    )
    password = serializers.CharField(
        label=('Password'),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=('Token'),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = get_object_or_404(User, email=email)
        if user.check_password(password):
            attrs['user'] = user
            return attrs
        else:
            msg = ('Unable to log in with provided credentials.')
            raise ValidationError(msg, code='authorization')


class UserRegSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя при регистрации'''

    class Meta(object):
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        '''Проверка пароля на правильность заполнения'''
        validate_password(value)
        return value

    def create(self, validated_data):
        '''Функция для скрытия пароля из отображения и хеширование в базе'''
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя(кроме регистрации)'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta(object):
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, follower):
        '''Проверка того, является ли пользователь нашим подписчиком'''
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, follower=follower).exists()
        return False


class ChangePasswordSerializer(serializers.Serializer):
    '''Сериализатор изменения пароля'''
    model = User

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        '''Проверка пароля на правильность заполнения'''
        validate_password(value)
        return value


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор тегов'''
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор промежуточной модели рецепта'''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class ShowRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор итогового отображения рецепта'''
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    def get_is_favorited(self, obj):
        '''Проверка того, находится ли рецепт в избранном'''
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipes=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Проверка того, находится ли рецепт в списке покупок'''
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipes=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта'''
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = RecipeIngredientSerializer(source='recipe', many=True)
    author = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ['author', 'name', 'image', 'text',
                  'tags', 'cooking_time', 'ingredients']

    def validate_cooking_time(self, attrs):
        if attrs > 0:
            return attrs
        raise ValidationError('Время приготовления должно быть больше единицы')

    def validate_tags(self, attrs):
        attr_set = set(attrs)
        if len(attrs) == len(attr_set):
            return attrs
        raise ValidationError('Теги должны быть уникальными')

    def validate_ingredients(self, attrs):
        id_list = []
        for attr in attrs:
            attr_amount = dict(attr)['amount']
            if attr_amount < 1:
                raise ValidationError('Количество должно быть больше нуля')
            id_list.append(dict(attr)['ingredient']['id'])
        id_list_set = set(id_list)
        if len(attrs) == len(id_list_set):
            return attrs
        raise ValidationError('Ингредиенты должны быть уникальными')

    def to_representation(self, instance):
        '''Изменение сериализатора отображения'''
        ret = OrderedDict()
        fields = ShowRecipeSerializer(instance, context=self.context)

        for field in fields:
            attribute = field.get_attribute(instance)
            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def add_ingredients(self, ingredients, recipes):
        for ingredient in ingredients:
            ingr_id = dict(ingredient)['ingredient']['id']
            amount = dict(ingredient)['amount']
            current_ingredient = get_object_or_404(Ingredient, id=ingr_id)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipes, amount=amount
            )
        return recipes

    def create(self, validated_data):
        '''Создание рецепта'''
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        return self.add_ingredients(ingredients, recipes)

    def update(self, instance, validated_data):
        '''Обновление рецепта'''
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        return self.add_ingredients(ingredients, instance)


class FollowRecipeSerialiser(serializers.ModelSerializer):
    '''Сериализатор рецепта для отображения при подписке'''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class IngredientSerialiser(serializers.ModelSerializer):
    '''Сериализатор ингредиентов'''
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class FavoriteSerialiser(serializers.ModelSerializer):
    '''Сериализатор отображения рецепта при добавлении в избранное'''

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор подписки на пользователя'''
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, user):
        '''Отображение рецептов того, на кого подписываемся'''
        limit = self.context['request'].GET.get('recipes_limit')
        if limit is not None:
            limit = int(limit)
            recipes = Recipe.objects.filter(author=user)[:limit]
        else:
            recipes = Recipe.objects.filter(author=user)
        serializer = FollowRecipeSerialiser(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, follower):
        '''Проверка того, является ли пользователь нашим подписчиком'''
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, follower=follower).exists()
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']
