# Generated by Django 5.2.1 on 2025-05-15 07:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('current_quantity', models.PositiveIntegerField(default=0, help_text='Current quantity in grams')),
                ('threshold_quantity', models.PositiveIntegerField(default=1000, help_text='Minimum threshold for warning in grams')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, help_text='Price per kg in local currency', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IngredientDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Quantity delivered in grams')),
                ('delivery_date', models.DateField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Ingredient deliveries',
                'ordering': ['-delivery_date'],
            },
        ),
        migrations.CreateModel(
            name='IngredientUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Quantity used in grams')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
