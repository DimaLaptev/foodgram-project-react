import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tag seeds'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='path to file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as jsonfile:
            tags = json.load(jsonfile)
            for tag in tags:
                Tag.objects.bulk_create([
                    Tag(slug=tag['slug'],
                    name=tag['name'],
                    color=tag['color'])
                ])

        self.stdout.write(self.style.SUCCESS('Import was successful!'))
