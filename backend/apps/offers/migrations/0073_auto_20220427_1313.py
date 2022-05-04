# Generated by Django 3.0.7 on 2022-04-27 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20220420_1358'),
        ('offers', '0072_auto_20220427_0757'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageOfferMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Languages')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offers.TranslationOffer')),
            ],
        ),
        migrations.RemoveField(
            model_name='translationoffer',
            name='languages',
         ),
        migrations.AddField(
            model_name='translationoffer',
            name='languages',
            field=models.ManyToManyField(blank=True, through='offers.LanguageOfferMap', to='accounts.Languages', verbose_name='Sprachen'),
        ),
    ]
