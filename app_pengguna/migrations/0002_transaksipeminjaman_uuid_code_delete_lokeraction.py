# Generated by Django 4.2.7 on 2023-11-12 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pengguna', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaksipeminjaman',
            name='uuid_code',
            field=models.CharField(default='', max_length=36, unique=True),
        ),
        migrations.DeleteModel(
            name='LokerAction',
        ),
    ]