import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Import ingredients from CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "filepath",
            type=str,
            help="Путь к CSV-файлу с ингредиентами"
        )

    def import_ingredients(self, filepath):
        with open(filepath, encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

    def handle(self, *args, **kwargs):
        filepath = kwargs["filepath"]
        self.import_ingredients(filepath)
        self.stdout.write(self.style.SUCCESS(
            "Ингредиенты успешно импортированы!"))
