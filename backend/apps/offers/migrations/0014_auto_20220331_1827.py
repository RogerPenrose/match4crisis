# Generated by Django 3.0.7 on 2022-03-31 18:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0013_auto_20220331_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 31, 18, 27, 34, 882846, tzinfo=utc), verbose_name='date published'),
        ),
    ]
