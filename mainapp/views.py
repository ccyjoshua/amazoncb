# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _

from mainapp.forms import ProductForm
from mainapp.models import Product


class SellerAddProductView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'mainapp.add_product'

    template_name = 'mainapp/seller_add_product.html'
    form_class = ProductForm
    success_url = '/'

    def form_valid(self, form):
        new_product = form.save(commit=False)
        new_product.seller_id = self.request.user
        try:
            new_product.save()
        except IntegrityError:
            form.add_error('name', _(u'Cannot use the same product name as before'))
            return super(SellerAddProductView, self).form_invalid(form)
        return super(SellerAddProductView, self).form_valid(form)


class SellerProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    # Sellers can view their products if they can add products
    permission_required = 'mainapp.add_product'

    template_name = 'mainapp/seller_product_list.html'
    paginate_by = 2
    ordering = '-updated_at'

    # Note that we cannot set queryset directly in class attribute
    # because "request" is not valid until the class is constructed
    def get_queryset(self):
        self.queryset = Product.objects.filter(seller_id=self.request.user.id)
        return super(SellerProductListView, self).get_queryset()
