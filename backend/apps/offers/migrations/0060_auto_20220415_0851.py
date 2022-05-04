# Generated by Django 3.0.7 on 2022-04-15 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0059_auto_20220414_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericoffer',
            name='offerTitle',
            field=models.TextField(default='offerDefaultTitle', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='accommodationoffer',
            name='typeOfResidence',
            field=models.CharField(choices=[('RO', 'Eigener Raum'), ('HO', 'Gesamte Wohnung / Haus'), ('SO', 'Sofa / Bed')], default='SO', max_length=2),
        ),
        migrations.AlterField(
            model_name='buerocraticoffer',
            name='helpType_buerocratic',
            field=models.CharField(choices=[('AM', 'Accompaniment'), ('LE', 'Legal'), ('OT', 'Andere')], default='AM', max_length=2),
        ),
        migrations.AlterField(
            model_name='childcareofferlongterm',
            name='gender_longterm',
            field=models.CharField(choices=[('NO', 'Keine Angabe'), ('FE', 'Weiblich'), ('MA', 'Männlich'), ('OT', 'Andere')], default='NO', max_length=2),
        ),
        migrations.AlterField(
            model_name='childcareoffershortterm',
            name='gender_shortterm',
            field=models.CharField(choices=[('NO', 'Keine Angabe'), ('FE', 'Weiblich'), ('MA', 'Männlich'), ('OT', 'Andere')], default='NO', max_length=2),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='offerType',
            field=models.CharField(choices=[('AC', 'Unterbringung'), ('TL', 'Übersetzung'), ('TR', 'Logistik'), ('BU', 'Bürokratie'), ('MP', 'Manneskraft'), ('CL', 'Kinderbetreuung Langzeit'), ('BA', 'Babysitting'), ('WE', 'Medizinische Hilfe'), ('JO', 'Job'), ('DO', 'Spende')], default='AC', max_length=2),
        ),
        migrations.AlterField(
            model_name='joboffer',
            name='jobType',
            field=models.CharField(choices=[('ACA', 'Akademische Hilfe'), ('ADM', 'Administration'), ('ADV', 'Fortbildung'), ('CON', 'Konferenzen und Events'), ('FAC', 'Anlagenbetrieb'), ('FIN', 'Finance und Buchhaltung'), ('GEN', 'Allgemeine Verwaltung'), ('HEA', 'Gesundheitsservices'), ('HUM', 'Personalwesen'), ('INF', 'IT'), ('INT', 'International Program and Services'), ('LEG', 'Jura'), ('LIB', 'BÜchereiverwaltung'), ('MAR', 'Marketing'), ('OFF', 'Büro / Verwaltung'), ('PER', 'Kunst und Museumsverwaltung'), ('PUB', 'Öffentliche Sicherheit'), ('RES', 'Forschung und Forschungsadministration'), ('SPO', 'Sport'), ('STU', 'Studentische Dienstleistungen'), ('HAN', 'Handwerk')], default='ACA', max_length=3),
        ),
        migrations.AlterField(
            model_name='welfareoffer',
            name='helpType_welfare',
            field=models.CharField(choices=[('ELD', 'Altenpflege'), ('DIS', 'Behindertenpflege'), ('PSY', 'Psychologische Hilfe')], default='ELD', max_length=3),
        ),
    ]
