# Generated by Django 3.0.7 on 2022-05-10 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0073_auto_20220427_1313'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transportationoffer',
            old_name='helpType_transport',
            new_name='helpType',
        ),
        migrations.RenameField(
            model_name='welfareoffer',
            old_name='helpType_welfare',
            new_name='helpType',
        ),
        migrations.RenameField(
            model_name='buerocraticoffer',
            old_name='helpType_buerocratic',
            new_name='helpType',
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Unterbringung'), ('TL', 'Übersetzung'), ('TR', 'Logistik'), ('BU', 'Bürokratie'), ('MP', 'Manneskraft'), ('CL', 'Kinderbetreuung'), ('WE', 'Medizinische Hilfe'), ('JO', 'Jobangebot')], default='AC', max_length=2),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='typeOfCar',
            field=models.CharField(choices=[('KW', 'Kleinwagen'), ('MW', 'Mittelklassewagen'), ('KM', 'Kombi'), ('SU', 'SUV'), ('MI', 'Minivan'), ('TR', 'Transporter')], default='KW', max_length=2),
        ),
    ]
