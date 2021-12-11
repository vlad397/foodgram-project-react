import csv

from api.models import Ingredient
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load ingredients data to DB'

    def handle(self, *args, **options):
        with open('api/data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=unit
                ) 
