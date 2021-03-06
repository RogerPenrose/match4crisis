# Generated by Django 3.0.7 on 2022-04-02 00:42

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0023_auto_20220401_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('genericOffer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='offers.GenericOffer')),
                ('jobType', models.CharField(choices=[('ACA', 'Academic Support'), ('ADM', 'Administration'), ('ADV', 'Advancement'), ('CON', 'Conference and Events'), ('FAC', 'Facility Operations'), ('FIN', 'Finance and Accounting'), ('GEN', 'General Administration'), ('HEA', 'Health Services'), ('HUM', 'Human Resources'), ('INF', 'Information Technology'), ('INT', 'International Program and Services'), ('LEG', 'Legal'), ('LIB', 'Library Administration'), ('MAR', 'Marketing, Communication and External Affairs'), ('OFF', 'Office and Admin Support'), ('PER', 'Performing Arts and Museum Administration'), ('PUB', 'Public Safety'), ('RES', 'Research and Program Admin'), ('SPO', 'Sports and Recreation'), ('STU', 'Student Services'), ('HAN', 'Handicraft profession')], default='ACA', max_length=3)),
                ('jobTitle', models.CharField(blank=True, max_length=128)),
                ('requirements', models.TextField(blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='childcareoffershortterm',
            old_name='numberOfChildren',
            new_name='numberOfChildrenToCare',
        ),
        migrations.AlterField(
            model_name='accomodationoffer',
            name='numberOfChildren',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='accomodationoffer',
            name='numberOfPets',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 2, 0, 41, 59, 392650, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Accomodation'), ('TL', 'Translation'), ('TR', 'Transportation'), ('BU', 'Buerocratic'), ('MP', 'Manpower'), ('CL', 'Childcare Permanent'), ('BA', 'Babysitting'), ('WE', 'Medical Assistance'), ('JO', 'Job')], default='AC', max_length=2),
        ),
    ]
