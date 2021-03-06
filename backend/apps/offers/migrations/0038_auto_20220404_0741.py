# Generated by Django 3.0.7 on 2022-04-04 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0037_auto_20220404_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('SO', 'Sofa / Bed'), ('HO', 'Whole Flat / House'), ('RO', 'Private Room')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='translationoffer',
            name='firstLanguage',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='translationoffer',
            name='secondLanguage',
            field=models.CharField(max_length=50),
        ),
    ]
