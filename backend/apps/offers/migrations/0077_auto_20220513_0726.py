# Generated by Django 3.0.7 on 2022-05-13 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0076_merge_20220513_0713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericoffer',
            name='location',
            field=models.TextField(default='Nordpol', max_length=300),
        ),
    ]
