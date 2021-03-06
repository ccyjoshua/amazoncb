# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-10 19:46
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0020_auto_20180102_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='avail_today',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='pending_order',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
