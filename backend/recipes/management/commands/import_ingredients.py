import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Import ingredients from CSV file"

    def import_ingredients(self, filepath):
        with open(filepath, encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

    def handle(self, *args, **kwargs):
        self.import_ingredients("data/ingredients.csv")
        self.stdout.write(self.style.SUCCESS(
            "Ингредиенты успешно импортированы!"))
