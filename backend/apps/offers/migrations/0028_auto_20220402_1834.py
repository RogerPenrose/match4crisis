# Generated by Django 3.0.7 on 2022-04-02 18:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0027_auto_20220402_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accomodationoffer',
            name='startDateAccomodation',
            field=models.DateField(default=datetime.datetime(2022, 4, 2, 18, 34, 41, 706832)),
        ),
        migrations.AlterField(
            model_name='accomodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('HO', 'Whole Flat / House'), ('SO', 'Sofa / Bed'), ('RO', 'Private Room')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 2, 18, 34, 41, 702395, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 2, 18, 34, 41, 707995)),
        ),
    ]
