# Generated by Django 3.0.7 on 2022-04-05 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20220331_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='languages',
            name='country',
            field=models.CharField(default='de', max_length=2),
            preserve_default=False,
        ),
    ]