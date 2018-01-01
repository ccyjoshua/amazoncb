# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-25 07:24
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_auto_20171223_1500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='orig_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='must_review',
        ),
        migrations.AddField(
            model_name='product',
            name='how_to_find',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
