# Generated by Django 3.0.7 on 2022-03-20 17:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('organisationName', models.CharField(default='', max_length=300)),
                ('contactPerson', models.CharField(default='', max_length=100)),
                ('clubNumber', models.CharField(default='0', max_length=20)),
                ('country', models.CharField(max_length=50)),
                ('postalCode', models.CharField(max_length=15)),
                ('streetNameAndNumber', models.CharField(max_length=50)),
                ('generalInfo', models.TextField(default='', max_length=10000)),
                ('isApproved', models.BooleanField(default=False)),
                ('approvalDate', models.DateTimeField(null=True)),
                ('appearsInMap', models.BooleanField(default=False)),
                ('acceptedPrivacyStatement', models.BooleanField(default=False)),
                ('acceptedDataSharing', models.BooleanField(default=False)),
                ('uuid', models.CharField(blank=True, default=uuid.uuid4, max_length=100, unique=True)),
                ('approvedBy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approvedBy', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
