# Generated by Django 3.0.7 on 2022-06-08 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0084_auto_20220603_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageclass',
            name='offerId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='images', to='offers.GenericOffer'),
        ),
    ]
