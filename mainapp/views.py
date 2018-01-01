# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
from django.urls import reverse
from time import sleep

from mainapp.forms import ProductForm
from mainapp.models import Product


class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='seller_group').exists():
                return reverse('seller_product_list')
            elif self.request.user.groups.filter(name='buyer_group').exists():
                return reverse('buyer_product_list')
            else:
                return '/'
        else:
            return reverse('account_signin')


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


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


# Make sure seller can only CRUD it's own product
class SellerQuerySetMixin(object):
    def get_object(self, queryset=None):
        queryset = Product.objects.filter(seller_id=self.request.user)
        return super(SellerQuerySetMixin, self).get_object(queryset=queryset)


class SellerUpdateStockView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, AjaxableResponseMixin, UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    fields = ['stock', 'limit_per_day']
    success_url = '/'  # not used


class SellerUpdateProductView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    template_name = 'mainapp/seller_update_product.html'
    fields = ['name', 'orig_price', 'discount', 'description', 'requirement', 'amazon_link', 'how_to_find', 'stock', 'limit_per_day']

    def get_success_url(self):
        self.success_url = reverse('seller_product_detail', args=[self.object.id])
        return super(SellerUpdateProductView, self).get_success_url()


class SellerUpdateImageView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, AjaxableResponseMixin, UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    fields = ['image']
    success_url = '/'  # not used


class SellerProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, DetailView):
    # Sellers can view their products if they can add products
    permission_required = 'mainapp.add_product'
    model = Product
    template_name = 'mainapp/seller_product_detail.html'
