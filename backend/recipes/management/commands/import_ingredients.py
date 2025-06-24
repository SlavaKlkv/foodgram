import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Import ingredients from CSV file"

    def handle(self, *args, **kwargs):
        with open("data/ingredients.csv", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
        self.stdout.write(self.style.SUCCESS(
            "Ингредиенты успешно импортированы!"))
