# Generated by Django 3.0.7 on 2022-04-19 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0061_auto_20220418_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transportationoffer',
            name='country',
        ),
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('HO', 'Gesamte Wohnung / Haus'), ('SO', 'Sofa / Bed'), ('RO', 'Eigener Raum')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='bb',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='lat',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='lng',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='location',
            field=models.TextField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerDescription',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerTitle',
            field=models.TextField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Unterbringung'), ('TL', 'Übersetzung'), ('TR', 'Logistik'), ('BU', 'Bürokratie'), ('MP', 'Manneskraft'), ('CL', 'Kinderbetreuung Langzeit'), ('BA', 'Babysitting'), ('WE', 'Medizinische Hilfe'), ('JO', 'Jobangebot'), ('DO', 'Spende')], default='AC', max_length=2),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='latEnd',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='transportationoffer',
            name='lngEnd',
            field=models.FloatField(null=True),
        ),
    ]
