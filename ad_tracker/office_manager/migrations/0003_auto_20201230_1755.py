# Generated by Django 3.1.4 on 2020-12-31 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0002_auto_20201230_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraiser',
            name='my_field_name',
            field=models.CharField(help_text='Enter appraiser name', max_length=20),
        ),
        migrations.AlterField(
            model_name='client',
            name='my_field_name',
            field=models.CharField(help_text='Enter client name', max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='my_field_name',
            field=models.CharField(help_text='Enter product description', max_length=20),
        ),
    ]