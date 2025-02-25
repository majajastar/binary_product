# Generated by Django 4.2.17 on 2024-12-21 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MinutePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
            ],
            options={
                'unique_together': {('product_type', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='HourPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
            ],
            options={
                'unique_together': {('product_type', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='FiveMinutePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
            ],
            options={
                'unique_together': {('product_type', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='FifteenMinutePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
            ],
            options={
                'unique_together': {('product_type', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='DayPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
            ],
            options={
                'unique_together': {('product_type', 'timestamp')},
            },
        ),
    ]
