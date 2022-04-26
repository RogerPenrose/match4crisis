# Generated by Django 3.0.7 on 2022-04-26 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0068_transportationoffer_helptype_transport'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportationoffer',
            name='typeOfCar',
            field=models.CharField(choices=[('KW', 'Kleinwagen'), ('MW', 'Mittelklassewagen'), ('KM', 'Kobi'), ('SU', 'SUV'), ('MI', 'Minivan'), ('TR', 'Transporter')], default='KW', max_length=2),
        ),
    ]