# Generated by Django 4.2.20 on 2025-06-21 12:19

import django.core.validators
from django.db import migrations, models

import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_alter_favorite_recipe_alter_recipe_cooking_time_and_more"), ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=core.fields.FromOneSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MinValueValidator(1),
                ],
                verbose_name="Время приготовления (в минутах)",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount",
            field=core.fields.FromOneSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MinValueValidator(1),
                ],
                verbose_name="Количество",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.SlugField(
                blank=True,
                default=1,
                max_length=32,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Слаг может содержать только латинские буквы, цифры, дефис и подчёркивание.",
                        regex="^[-a-zA-Z0-9_]+$",
                    )
                ],
                verbose_name="Слаг",
            ),
            preserve_default=False,
        ),
    ]
