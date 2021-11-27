from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import CASCADE

from .data import HEX, UNITS


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={'unique': ('A user with that email already exists.')}
    )

    username = models.TextField(max_length=150, unique=True)
    first_name = models.TextField(max_length=150, unique=True)
    last_name = models.TextField(max_length=150, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(choices=UNITS, max_length=200)

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=150, unique=True)
    color = models.CharField(choices=HEX, max_length=500)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='recipes/', null=True)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipe_ingredients',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tags, related_name='recipe_teg')
    cooking_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=CASCADE, related_name='ingredient',
        blank=True, null=True
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=CASCADE, related_name='recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'{self.recipes}: {self.ingredient} количеством {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite_recipes'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner"
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart_recipes'
    )
