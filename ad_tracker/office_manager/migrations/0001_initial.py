# Generated by Django 3.1.4 on 2020-12-31 01:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appraiser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(max_length=255)),
                ('FNMA_form', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(max_length=50)),
                ('l_name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(default='admin', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.FloatField(blank=True, default=0.0)),
                ('tech_fee', models.FloatField(blank=True, default=0.0)),
                ('address', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, max_length=500, null=True)),
                ('due_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('A', 'Assigned'), ('H', 'On Hold'), ('IR', 'Info Requested'), ('X', 'Cancelled'), ('C', 'Completed')], default='Assigned', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adding_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_orders', to='office_manager.user')),
                ('assigned_appraiser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to='office_manager.appraiser')),
                ('client_ordered', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_placed', to='office_manager.client')),
                ('product_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_of_type', to='office_manager.product')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]