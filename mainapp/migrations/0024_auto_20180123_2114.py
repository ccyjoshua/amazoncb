# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-24 05:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0023_auto_20180123_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='must_review',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='review_requirement',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]