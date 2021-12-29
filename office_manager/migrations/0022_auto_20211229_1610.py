# Generated by Django 3.1.4 on 2021-12-29 22:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0021_auto_20210204_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraiser',
            name='insurance_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 12, 29, 16, 10, 39, 67365)),
        ),
        migrations.AlterField(
            model_name='appraiser',
            name='license_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 12, 29, 16, 10, 39, 67338)),
        ),
        migrations.AlterField(
            model_name='client',
            name='last_ordered',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 12, 29, 16, 10, 39, 68239)),
        ),
    ]
