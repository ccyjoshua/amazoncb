# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os.path

# Create your models here.
User = get_user_model()


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{0}.{1}'.format(uuid.uuid4(), ext)
    user_path = 'user_' + str(instance.seller_id.id)
    return os.path.join(user_path, filename)


class Product(models.Model):
    class Meta:
        permissions = (("view_product", "Can View Product"),)
        unique_together = (("seller_id", "name"),)

    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.FloatField(default=1, validators=[MinValueValidator(0), MaxValueValidator(1)])  # 100% off
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to=user_directory_path)
    requirement = models.TextField(blank=True, max_length=500)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    limit_per_day = models.IntegerField(validators=[MinValueValidator(0)])
    completed = models.IntegerField(default =0)
    ordered = models.IntegerField(default=0)
    reviewed = models.IntegerField(default=0)
    must_review = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Purchase(models.Model):
    ORDERED_STATUS = 1
    ORDER_VERIFIED_STATUS = 2
    REVIEWED_STATUS = 3
    REVIEW_VERIFIED_STATUS = 4
    STATUS_CHOICES = (
        (ORDERED_STATUS, 'Ordered'),
        (ORDER_VERIFIED_STATUS, 'Order Verified'),
        (REVIEWED_STATUS, 'Reviewed'),
        (REVIEW_VERIFIED_STATUS, 'Review Verified'),
    )
    order_number = models.CharField(max_length=50)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=ORDERED_STATUS)
    order_screenshot = models.ImageField()
    review_screenshot = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
