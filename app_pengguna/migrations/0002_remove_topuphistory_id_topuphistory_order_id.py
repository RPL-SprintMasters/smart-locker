# Generated by Django 4.2.7 on 2023-11-29 05:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_pengguna', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topuphistory',
            name='id',
        ),
        migrations.AddField(
            model_name='topuphistory',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
