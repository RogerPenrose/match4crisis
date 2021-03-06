# Generated by Django 3.0.7 on 2022-06-13 22:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0086_auto_20220613_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodationoffer',
            name='numberOfPeople',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Anzahl Personen'),
        ),
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('SO', 'Sofa / Bett'), ('RO', 'Eigener Raum'), ('HO', 'Gesamte Wohnung / Haus')], default='SO', max_length=2, verbose_name='Art der Unterkunft'),
        ),
        migrations.AlterField(
            model_name='childcareoffer',
            name='numberOfChildren',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Anzahl Kinder'),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='numberOfPassengers',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Anzahl freier Plätze'),
        ),
    ]
