import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import indegrient seeds'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='path to file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as jsonfile:
            ingredients = json.load(jsonfile)
            for ingredient in ingredients:
                Ingredient.objects.bulk_create([
                    Ingredient(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'])
                ])

        self.stdout.write(self.style.SUCCESS('Import was successful'))
