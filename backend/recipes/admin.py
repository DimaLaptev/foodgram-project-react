from django.contrib import admin

from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    FavoriteRecipe,
    RecipeList,
    ShoppingCart,
    Tag,
)


EMPTY_STRING: str = '-empty-'


class RecipeIngredientsAdmin(admin.StackedInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)


@admin.register(RecipeList)
class RecipeListAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsAdmin,)
    list_display = ('author', 'name', 'text', 'get_favorite_count')
    search_fields = (
        'name', 'cooking_time',
        'author__username', 'ingredients__name'
    )
    list_filter = (
        'pub_date', 'tags',
    )
    empty_value_display = EMPTY_STRING

    @admin.display(
        description='email of author'
    )
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Tags')
    def get_tags(self, obj):
        return ', '.join(str(tag) for tag in obj.tags.all())

    @admin.display(description='ingredients')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @admin.display(description='In favorite')
    def get_favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_STRING


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',)
    search_fields = (
        'name', 'measurement_unit',)
    empty_value_display = EMPTY_STRING


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')
    empty_value_display = EMPTY_STRING


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')
    empty_value_display = EMPTY_STRING
