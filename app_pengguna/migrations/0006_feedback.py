# Generated by Django 4.2.7 on 2023-12-01 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_pengguna', '0005_alter_notifikasi_pembuat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
                ('message', models.TextField()),
                ('transaksi', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app_pengguna.transaksipeminjaman')),
            ],
        ),
    ]