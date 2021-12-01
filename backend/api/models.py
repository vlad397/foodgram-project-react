from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import CASCADE

from .data import HEX, UNITS


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={'unique': ('A user with that email already exists.')},
        verbose_name='Почта'
    )

    username = models.TextField(
        max_length=150, unique=True, verbose_name='Никнейм'
    )
    first_name = models.TextField(
        max_length=150, unique=True, verbose_name='Имя'
    )
    last_name = models.TextField(
        max_length=150, unique=True, verbose_name='Фамилия'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150, verbose_name='Название ингредиениа'
    )
    measurement_unit = models.CharField(
        choices=UNITS, max_length=200, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=150, unique=True, verbose_name='Название тега'
    )
    color = models.CharField(
        choices=HEX, max_length=500, verbose_name='Цвет тега'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг тега')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=150, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/', null=True, verbose_name='Картинка рецепта'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=CASCADE,
        blank=True, null=True,
        verbose_name='Ингредиент рецепта промежуточной модели'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=CASCADE, related_name='recipe_ingredients',
        verbose_name='Рецепт промежуточной модели'
    )
    # Добавил человекочитаемое сообщение, однако выводится все равно встроенное
    # Пытался явно задавать message= или просто писать само сообщение, писать
    # сообщение в скобках(как в самом валидаторе) и без.
    # Ничего не работает, хотя по документации должно работать.
    # В слаке мне не смогли подсказать, в нете решения не нашел (может плохо
    # искал). Было одно англоязычное обсуждение по этому вопросу, но там 
    # сошлись на том, что сойдет и встроенное сообщение (видимо потому что они 
    # и так все понимают).
    # Может Вы подскажете, в чем может быть проблема? Или наследовать и 
    # изменять сообщение в кастомном валидаторе?
    # П.с. миграции применял при каждом изменении =)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message=('Минимум единица'))],
        verbose_name='Количество ингредиента промежуточной модели'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта (промжуточная модель)'
        verbose_name_plural = 'Ингредиенты рецепта (промежуточная модель)'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} количеством {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_recipes',
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite_recipes',
        verbose_name='Избранный ингредиент'
    )

    class Meta:
        verbose_name = 'Избранный ингредиент'
        verbose_name_plural = 'Избранные ингредиенты'
        constraints = [models.UniqueConstraint(fields=['user', 'recipes'],
                       name='unique_favorite_recipe')]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following",
        verbose_name='Пользователь'
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower",
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Избранные авторы'
        constraints = [models.UniqueConstraint(fields=['user', 'follower'],
                       name='unique_follower')]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner",
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart_recipes',
        verbose_name='Список покупок'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipes'],
                       name='unique_shopping_cart_recipe')]
