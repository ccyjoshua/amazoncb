# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-26 01:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_product_amazon_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='amazon_link',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]