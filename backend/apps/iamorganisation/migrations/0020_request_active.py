# Generated by Django 3.0.7 on 2022-07-14 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iamorganisation', '0019_materialdonationrequest_donationtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Ist aktiv'),
        ),
    ]