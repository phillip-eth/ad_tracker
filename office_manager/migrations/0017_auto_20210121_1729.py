# Generated by Django 3.1.4 on 2021-01-22 01:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0016_auto_20210121_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='appraiser',
            name='license_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 17, 29, 57, 514941)),
        ),
        migrations.AlterField(
            model_name='appraiser',
            name='insurance_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 17, 29, 57, 514941)),
        ),
        migrations.AlterField(
            model_name='client',
            name='last_ordered',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 17, 29, 57, 515937)),
        ),
    ]
