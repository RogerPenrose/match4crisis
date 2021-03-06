# Generated by Django 3.0.7 on 2022-03-31 15:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0012_auto_20220331_0723'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accomodationoffer',
            old_name='numberOfInhabitants',
            new_name='numberOfAdults',
        ),
        migrations.RemoveField(
            model_name='accomodationoffer',
            name='petsAllowed',
        ),
        migrations.AddField(
            model_name='accomodationoffer',
            name='numberOfChildren',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='accomodationoffer',
            name='numberOfPets',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='accomodationoffer',
            name='typeOfResidence',
            field=models.CharField(default='SO', max_length=2, verbose_name={('SO', 'Sofa / Bed'), ('HO', 'Whole Flat / House'), ('RO', 'Private Room')}),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 31, 15, 43, 35, 469122, tzinfo=utc), verbose_name='date published'),
        ),
    ]
