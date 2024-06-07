# Generated by Django 5.0 on 2024-06-07 21:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mesas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resultados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivoResultado', models.FileField(upload_to='resultados')),
                ('mesa', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='mesas.mesa')),
            ],
        ),
    ]