# Generated by Django 3.0.7 on 2022-04-14 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0058_auto_20220413_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('HO', 'Whole Flat / House'), ('RO', 'Private Room'), ('SO', 'Sofa / Bed')], default='SO', max_length=2),
        ),
    ]
