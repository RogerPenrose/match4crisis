# Generated by Django 3.0.7 on 2022-03-23 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fullName',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
