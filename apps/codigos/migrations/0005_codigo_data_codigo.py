# Generated by Django 5.0 on 2024-03-28 23:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codigos', '0004_alter_codigo_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='codigo',
            name='data_codigo',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
