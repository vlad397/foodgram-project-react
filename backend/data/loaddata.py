import csv
import os
import sys

import django

sys.path.append('../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()


def load_all_data(func):

    from api.models import Ingredient

    func('ingredients.csv', Ingredient)
    print('\nИнгридиенты загружены\n')


@load_all_data
def load_table_from_csv(fname, model):
    from api.models import Ingredient
    file = open(fname, 'r', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    Ingredient.objects.create(
            name='абрикосовое варенье', measurement_unit='г')
    for row in reader:
        Ingredient.objects.create(
            name=row['абрикосовое варенье'], measurement_unit=row['г'])
        print(f'{row}')

