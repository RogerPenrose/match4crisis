# Generated by Django 3.0.7 on 2022-03-29 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0008_merge_20220329_0921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genericoffer',
            name='image',
        ),
    ]
