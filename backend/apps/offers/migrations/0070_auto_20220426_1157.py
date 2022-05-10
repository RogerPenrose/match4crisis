# Generated by Django 3.0.7 on 2022-04-26 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0069_transportationoffer_typeofcar'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChildcareOffer',
            fields=[
                ('genericOffer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='offers.GenericOffer')),
                ('isRegular', models.BooleanField(default=False)),
                ('hasExperience', models.BooleanField(default=False)),
                ('hasEducation', models.BooleanField(default=False)),
                ('hasSpace', models.BooleanField(default=False)),
                ('distance', models.IntegerField(default=5)),
                ('numberOfChildren', models.IntegerField(default=1)),
                ('helpType_childcare', models.CharField(choices=[('GT', 'Ganztagesbetruung'), ('HT', 'Halbtagsbetreuung'), ('WE', 'Wochendendbetreuung')], default='GT', max_length=2)),
                ('timeOfDay', models.CharField(choices=[('VM', 'Vormittags'), ('NM', 'Nachmittags'), ('AB', 'Abends')], default='VM', max_length=2)),
            ],
        ),
        migrations.RemoveField(
            model_name='childcareoffershortterm',
            name='genericOffer',
        ),
        migrations.RemoveField(
            model_name='transportationoffer',
            name='date',
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Unterbringung'), ('TL', 'Übersetzung'), ('TR', 'Logistik'), ('BU', 'Bürokratie'), ('MP', 'Manneskraft'), ('CL', 'Kinderbetreuung'), ('WE', 'Medizinische Hilfe'), ('JO', 'Jobangebot'), ('DO', 'Spende')], default='AC', max_length=2),
        ),
        migrations.DeleteModel(
            name='ChildcareOfferLongterm',
        ),
        migrations.DeleteModel(
            name='ChildcareOfferShortterm',
        ),
    ]