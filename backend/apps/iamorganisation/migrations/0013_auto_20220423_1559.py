# Generated by Django 3.0.7 on 2022-04-23 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iamorganisation', '0012_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationrequest',
            name='donationGoal',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]