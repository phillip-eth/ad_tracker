# Generated by Django 3.1.4 on 2021-01-10 01:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('office_manager', '0005_auto_20210108_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['status', 'due_date']},
        ),
    ]
