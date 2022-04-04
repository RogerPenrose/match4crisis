# Generated by Django 3.0.7 on 2022-04-03 23:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0033_auto_20220403_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodationoffer',
            name='startDateAccommodation',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 23, 25, 7, 345909)),
        ),
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('HO', 'Whole Flat / House'), ('SO', 'Sofa / Bed'), ('RO', 'Private Room')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 3, 23, 25, 7, 341877, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 23, 25, 7, 346970)),
        ),
    ]