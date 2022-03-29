# Generated by Django 3.0.7 on 2022-03-23 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iamorganisation', '0003_auto_20220322_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='clubNumber',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='country',
            field=models.CharField(choices=[('DE', 'Deutschland'), ('PL', 'Polen'), ('AT', 'Österreich')], max_length=50),
        ),
    ]
