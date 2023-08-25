from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from djoser.serializers import UserSerializer as UserHandleSerializer
from rest_framework import serializers, validators
from rest_framework.generics import get_object_or_404

from api.services import Base64ImageField
from core import constants
from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    FavoriteRecipe,
    RecipeList,
    ShoppingCart,
    Tag,
)
from users.models import Subscribe


User = get_user_model()


class UserSerializer(UserHandleSerializer):
    '''processing of user data'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        '''check of subsribe'''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=obj.id).exists()


class UserPasswordSerializer(serializers.Serializer):
    '''change password serializer'''
    new_password = serializers.CharField(
        label='new password')
    current_password = serializers.CharField(
        label='current password')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                'Unable to log in. '
                'Credentials are outdated.',
                code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    '''Tag serializer'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Ingredient serializer'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    '''Serializer of IngredientInRecipe-model'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=('ingredient', 'recipe'),
            )
        ]


class FavoriteOrSubscribeSerializer(serializers.ModelSerializer):
    '''Serializer of favorite or subscribe'''
    image = Base64ImageField()

    class Meta:
        model = RecipeList
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    '''Serializer of subscribers'''
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('is_subscribed', 'recipes_count',)

    def validate(self, data):
        '''Validate of data'''
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError({
                'errors': 'Error! You cant subscribe to yourself.'
            })
        if Subscribe.objects.filter(user=user_id,
                                    author=author_id).exists():
            raise serializers.ValidationError({
                'errors': 'Error! Re-subscribe.'
            })
        data['user'] = get_object_or_404(User, id=user_id)
        data['author'] = get_object_or_404(User, id=author_id)
        return data

    def get_is_subscribed(self, obj):
        '''check of subscribe'''
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        '''get recipes'''
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = RecipeList.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = FavoriteOrSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        '''recipes count'''
        return RecipeList.objects.filter(author=obj.author).count()


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer of recipe'''
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True
    )
    cooking_time = serializers.IntegerField()
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = RecipeList
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    @staticmethod
    def __create_ingredients(recipe, ingredients):
        '''creating a temporary table for recipes'''
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe,
             ingredient_id=ingredient.get('id'),
             amount=ingredient.get('amount'))
             for ingredient in ingredients])

    def create(self, validated_data):
        '''creating a recipe'''
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = RecipeList.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.__create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        '''update of recipe'''
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.__create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        '''check recipe in favorite list'''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=obj,
                                             user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        '''check the shopping cart'''
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=user).exists()

    def validate(self, data):
        '''validation of serializer-data'''
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Add at least one ingredient for the recipe')
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) < constants.MIN_INGREDIENT_AMOUNT:
                errors.append(
                    f'The amount of the ingredient with id {ingredient["id"]} '
                    f'must be whole and not less than '
                    f'{constants.MIN_INGREDIENT_AMOUNT}.'
                )
            if ingredient['id'] in added_ingredients:
                errors.append(
                    'You cannot put the same ingredient in the recipe twice'
                )
            added_ingredients.append(ingredient['id'])
        tags = data.get('tags')
        if len(tags) > len(set(tags)):
            errors.append('The same tag cannot be applied twice.')
        cooking_time = float(data.get('cooking_time'))
        if cooking_time < constants.MIN_COOKING_TIME:
            errors.append(
                f'The cooking time should be at least '
                f'{constants.constants.MIN_COOKING_TIME} minute.'
            )
        if cooking_time > constants.MAX_COOKING_TIME:
            errors.append(
                f'The cooking time should not be longer '
                f'{constants.MAX_COOKING_TIME} minute.'
            )
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data
