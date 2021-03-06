# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-24 05:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0022_product_ordered_today'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='requirement',
            new_name='order_requirement',
        ),
        migrations.AlterField(
            model_name='purchase',
            name='status',
            field=models.IntegerField(choices=[(1, 'Ordered Pending Verify'), (2, 'Pending Review'), (3, 'Pending Review Verify'), (4, 'Pending Delivery'), (5, 'Pending Delivery Verify'), (6, 'Pending Payment'), (7, 'Completed')], default=1),
        ),
    ]
