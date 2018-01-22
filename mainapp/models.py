# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os.path
from decimal import *
from validators import AmazonURLValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
User = get_user_model()


def product_user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{0}.{1}'.format(uuid.uuid4(), ext)
    user_path = 'user_' + str(instance.seller_id.id)
    return os.path.join(user_path, filename)


def purchase_user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{0}.{1}'.format(uuid.uuid4(), ext)
    user_path = 'user_' + str(instance.buyer_id.id)
    return os.path.join(user_path, filename)


@python_2_unicode_compatible
class Product(models.Model):
    class Meta:
        permissions = (("view_product", "Can View Product"),)
        unique_together = (("seller_id", "name"),)

    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    orig_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  # percentage off
    description = models.TextField(max_length=5000)
    image = models.ImageField(upload_to=product_user_directory_path)
    requirement = models.TextField(blank=True, max_length=500)
    amazon_link = models.URLField(blank=True, max_length=500, validators=[
        AmazonURLValidator(message=_('Domain must be Amazon'), code='invalid_domain')])
    how_to_find = models.TextField(blank=True, max_length=500)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    limit_per_day = models.IntegerField(validators=[MinValueValidator(0)])
    avail_today = models.IntegerField(validators=[MinValueValidator(0)])
    pending_order = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    ordered = models.IntegerField(default=0)
    reviewed = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    ordered_today = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def description_as_list(self):
        return self.description.split('\n')

    def requirement_as_list(self):
        return self.requirement.split('\n')

    @property
    def sale_price(self):
        sale_price = Decimal(self.orig_price) * Decimal((100 - self.discount) / 100.)
        return sale_price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.name + ', seller: ' + self.seller_id.username


@python_2_unicode_compatible
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
    order_screenshot = models.ImageField(upload_to=purchase_user_directory_path)
    review_screenshot = models.ImageField(upload_to=purchase_user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Product ' + str(self.product_id.id).encode("utf-8").decode("utf-8") + ', buyer: ' + self.buyer_id.username
