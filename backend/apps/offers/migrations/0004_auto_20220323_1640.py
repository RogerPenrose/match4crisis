# Generated by Django 3.0.7 on 2022-03-23 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0003_remove_genericoffer_createdby'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericoffer',
            name='image',
            field=models.ImageField(default='no-img.png', upload_to='users/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='streetName',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='genericoffer',
            name='streetNumber',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]