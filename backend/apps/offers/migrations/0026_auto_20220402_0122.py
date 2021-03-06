# Generated by Django 3.0.7 on 2022-04-02 01:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0025_auto_20220402_0104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accomodationoffer',
            name='stayLength',
        ),
        migrations.AddField(
            model_name='accomodationoffer',
            name='endDateAccomodation',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 4, 2, 1, 22, 28, 487484)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accomodationoffer',
            name='startDateAccomodation',
            field=models.DateField(default=datetime.datetime(2022, 4, 2, 1, 22, 22, 171019)),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 2, 1, 22, 22, 166714, tzinfo=utc), verbose_name='date published'),
        ),
    ]
