# Generated by Django 3.0.7 on 2022-04-12 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0051_auto_20220412_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('HO', 'Whole Flat / House'), ('SO', 'Sofa / Bed'), ('RO', 'Private Room')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='bb',
            field=models.CharField(max_length=300),
        ),
    ]
