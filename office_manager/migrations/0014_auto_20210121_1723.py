# Generated by Django 3.1.4 on 2021-01-22 01:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0013_auto_20210121_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraiser',
            name='insurance_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 17, 23, 57, 962059)),
        ),
        migrations.AlterField(
            model_name='client',
            name='last_ordered',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 17, 23, 57, 963061)),
        ),
    ]
