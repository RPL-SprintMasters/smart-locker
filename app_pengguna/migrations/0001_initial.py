# Generated by Django 4.2.7 on 2023-11-10 03:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupLoker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_loker', models.CharField(max_length=15)),
                ('alamat_loker', models.CharField(max_length=15)),
                ('harga_loker', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Loker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomor_loker', models.IntegerField(default=0)),
                ('status_loker', models.BooleanField(default=False)),
                ('grup_loker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pengguna.gruploker')),
            ],
        ),
        migrations.CreateModel(
            name='TransaksiPeminjaman',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mulaipinjam', models.DateField(auto_now=True)),
                ('akhirpinjam', models.DateField(auto_now=True)),
                ('total_harga', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(max_length=15)),
                ('loker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pengguna.loker')),
                ('pengguna', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.pengguna')),
            ],
        ),
        migrations.CreateModel(
            name='TopupHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=15)),
                ('tanggal', models.DateField(auto_now=True)),
                ('nominal', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('metode_pembayaran', models.CharField(max_length=15)),
                ('pengguna', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.pengguna')),
            ],
        ),
        migrations.CreateModel(
            name='Notifikasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('waktu', models.DateField(auto_now=True)),
                ('judul', models.CharField(max_length=15)),
                ('pesan', models.TextField()),
                ('pembuat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.admin')),
                ('pengguna', models.ManyToManyField(to='authentication.pengguna')),
            ],
        ),
        migrations.CreateModel(
            name='LokerAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid_code', models.CharField(max_length=36)),
                ('command', models.CharField(max_length=10)),
                ('img_name', models.CharField(default='', max_length=36)),
                ('loker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pengguna.loker')),
                ('pengguna', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.pengguna')),
            ],
        ),
    ]
