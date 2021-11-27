from collections import OrderedDict

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tags, User)


class NewAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=("Token"),
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

    class Meta(object):
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(object):
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, follower):
        user = self.context['request'].user
        if user.is_authenticated:
            if Follow.objects.filter(user=user, follower=follower).exists():
                return True
            return False
        return False


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class ShowRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipe', many=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if Favorite.objects.filter(user=user, recipes=obj).exists():
                return True
            return False
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if ShoppingCart.objects.filter(user=user, recipes=obj).exists():
                return True
            return False
        return False

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = RecipeIngredientSerializer(source='recipe', many=True)
    author = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ['author', 'name', 'image', 'text',
                  'tags', 'cooking_time', 'ingredients']

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = ShowRecipeSerializer(instance, context=self.context)

        for field in fields:
            attribute = field.get_attribute(instance)
            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        for ingredient in ingredients:
            id = dict(ingredient)['ingredient']['id']
            amount = dict(ingredient)['amount']
            current_ingredient = Ingredient.objects.get(id=id)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipes=recipes, amount=amount
            )
        return recipes

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in ingredients:
            id = dict(ingredient)['ingredient']['id']
            amount = dict(ingredient)['amount']
            current_ingredient = Ingredient.objects.get(id=id)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipes=instance, amount=amount
            )
        return instance


class FollowRecipeSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class IngredientSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class FavoriteSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, user):
        limit = self.context['request'].GET.get('recipes_limit')
        if limit is not None:
            limit = int(limit)
            recipes = Recipe.objects.filter(author=user)[:limit]
        else:
            recipes = Recipe.objects.filter(author=user).all()
        serializer = FollowRecipeSerialiser(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, follower):
        user = self.context['request'].user
        if user.is_authenticated:
            if Follow.objects.filter(user=user, follower=follower).exists():
                return True
            return False
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']
