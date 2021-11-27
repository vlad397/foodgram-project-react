import io

from django.conf import settings
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import CustomFilter
from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tags, User)
from .pagination import CustomPaginator
from .permissions import CustomUserPermission
from .serializers import (ChangePasswordSerializer, FollowRecipeSerialiser,
                          FollowSerializer, IngredientSerialiser,
                          NewAuthTokenSerializer, RecipeSerializer,
                          TagSerializer, UserRegSerializer, UserSerializer)


class NewObtainAuthToken(APIView):
    serializer_class = NewAuthTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = NewAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        print(type(token.key))
        return Response({'auth_token': token.key})


class UserView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.RetrieveModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegSerializer
    pagination_class = CustomPaginator
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] == 'me' and request.user.is_authenticated:
            instance = request.user
        elif kwargs['pk'] == 'me' and request.user.is_anonymous:
            return Response(
                {'errors': 'Вы не авторизованы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            instance = self.get_object()
        serializer = UserSerializer(instance, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=['get'], detail=False, permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        follower = request.user
        followers = Follow.objects.filter(follower=follower).all()
        users = User.objects.filter(following__in=followers).all()

        page = self.paginate_queryset(users)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['get', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        follower = request.user
        user = User.objects.get(id=int(kwargs['pk']))
        if request.method == 'GET':
            if follower == user:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, follower=follower).exists():
                return Response(
                    {'errors': 'Вы не можете подписаться дважды'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                Follow.objects.create(user=user, follower=follower)
                serializer = FollowSerializer(
                    user, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if Follow.objects.filter(user=user, follower=follower).exists():
                Follow.objects.filter(user=user, follower=follower).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=['post'], detail=False, permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        obj = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.data.get("current_password")
            if not obj.check_password(current_password):
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            obj.set_password(serializer.data.get("new_password"))
            obj.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [CustomUserPermission]

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_201_CREATED)


class RecipeView(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPaginator
    permission_classes = [CustomUserPermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RecipeSerializer(instance, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=['get', 'delete'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe = Recipe.objects.get(id=int(kwargs['pk']))
        if request.method == 'GET':
            if Favorite.objects.filter(user=user, recipes=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                Favorite.objects.create(user=user, recipes=recipe)
                serializer = FollowRecipeSerialiser(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if Favorite.objects.filter(user=user, recipes=recipe).exists():
                Favorite.objects.filter(user=user, recipes=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Запрашиваемый рецепт не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=['get', 'delete'], detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = Recipe.objects.get(id=int(kwargs['pk']))
        if request.method == 'GET':
            if ShoppingCart.objects.filter(user=user, recipes=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                ShoppingCart.objects.create(user=user, recipes=recipe)
                serializer = FollowRecipeSerialiser(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipes=recipe).exists():
                ShoppingCart.objects.filter(user=user, recipes=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Запрашиваемый рецепт не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=['get', 'delete'], detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shop_obj = ShoppingCart.objects.filter(user=user).all()
        cart = {}

        for obj in shop_obj:
            current_recipe = RecipeIngredient.objects.filter(
                recipes=obj.recipes
            )
            for ingredient in current_recipe:
                name = ingredient.ingredient.name
                unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if f'{name}, ({unit})' in cart.keys():
                    cart[f'{name}, ({unit})'] += amount
                else:
                    cart[f'{name}, ({unit})'] = amount

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        fonts_path = (str(settings.BASE_DIR) + '/api/fonts/')
        print(fonts_path)
        pdfmetrics.registerFont(
            ttfonts.TTFont('Arial', f'{fonts_path}arial.ttf')
        )
        pdfmetrics.registerFont(
            ttfonts.TTFont('Arial-Bold', f'{fonts_path}arialbd.ttf')
        )
        p.setFont('Arial-Bold', 14)
        p.drawString(250, 800, 'Список покупок:')
        x, y = 30, 770
        p.setFont('Arial', 14)
        for elem in cart:
            p.drawString(x, y, f'• {elem} - {cart[elem]}')
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )


class TagsView(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientsView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
