# Generated by Django 3.0.7 on 2022-04-03 13:20

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0031_auto_20220403_1256'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccommodationOffer',
            fields=[
                ('genericOffer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='offers.GenericOffer')),
                ('numberOfAdults', models.IntegerField(default=2)),
                ('numberOfChildren', models.IntegerField(blank=True, default=0)),
                ('numberOfPets', models.IntegerField(blank=True, default=0)),
                ('typeOfResidence', models.CharField(choices=[('SO', 'Sofa / Bed'), ('RO', 'Private Room'), ('HO', 'Whole Flat / House')], default='SO', max_length=2)),
                ('streetName', models.CharField(blank=True, max_length=200)),
                ('streetNumber', models.CharField(blank=True, max_length=4)),
                ('startDateAccommodation', models.DateField(default=datetime.datetime(2022, 4, 3, 13, 20, 31, 733083))),
                ('endDateAccommodation', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 3, 13, 20, 31, 729272, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Accommodation'), ('TL', 'Translation'), ('TR', 'Transportation'), ('BU', 'Buerocratic'), ('MP', 'Manpower'), ('CL', 'Childcare Permanent'), ('BA', 'Babysitting'), ('WE', 'Medical Assistance'), ('JO', 'Job'), ('DO', 'Donation')], default='AC', max_length=2),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 13, 20, 31, 734121)),
        ),
        migrations.DeleteModel(
            name='AccomodationOffer',
        ),
    ]
