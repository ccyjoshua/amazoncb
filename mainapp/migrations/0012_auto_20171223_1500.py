# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-23 23:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_auto_20171212_2311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(max_length=5000),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=500),
        ),
    ]
