# Generated by Django 3.0.7 on 2022-03-31 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iamorganisation', '0004_auto_20220323_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='generalInfo',
            field=models.TextField(blank=True, default='', max_length=10000),
        ),
    ]
