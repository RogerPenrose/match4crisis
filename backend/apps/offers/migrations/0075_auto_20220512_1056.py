# Generated by Django 3.0.7 on 2022-05-12 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0074_auto_20220510_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buerocraticoffer',
            name='helpType',
            field=models.CharField(choices=[('AM', 'Begleitung'), ('LE', 'Juristische Hilfe'), ('OT', 'Andere Bürokratische Hilfe')], default='AM', max_length=2),
        ),
        migrations.AlterField(
            model_name='childcareoffer',
            name='helpType_childcare',
            field=models.CharField(choices=[('GT', 'Ganztagsbetreuung'), ('HT', 'Halbtagsbetreuung'), ('WE', 'Wochendendsbetreuung')], default='GT', max_length=2),
        ),
    ]
