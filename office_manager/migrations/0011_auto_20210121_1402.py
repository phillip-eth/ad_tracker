# Generated by Django 3.1.4 on 2021-01-21 22:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0010_auto_20210121_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appraiser',
            name='sick_days_start',
        ),
        migrations.RemoveField(
            model_name='appraiser',
            name='sick_days_used',
        ),
        migrations.RemoveField(
            model_name='appraiser',
            name='vacation_days_start',
        ),
        migrations.RemoveField(
            model_name='appraiser',
            name='vacation_days_used',
        ),
        migrations.AddField(
            model_name='appraiser',
            name='insurance_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appraiser',
            name='license_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appraiser',
            name='insurance_exp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 14, 2, 9, 849262)),
        ),
        migrations.AlterField(
            model_name='client',
            name='last_ordered',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 21, 14, 2, 9, 850260)),
        ),
    ]
