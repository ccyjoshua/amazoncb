# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import F
from collections import defaultdict
from time import time

from mainapp.forms import ProductForm
from mainapp.models import Product, Purchase
from apps import schedule

# Buyer request order time limit in minutes
EXPIRATION_TIME = 1  # FIXME
# Store pending order as {product_id: {user_id: time}}
pending_order_map = defaultdict(dict)


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
        new_product.avail_today = min(new_product.stock, new_product.limit_per_day)
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


class SellerUpdateStockView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, AjaxableResponseMixin,
                            UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    fields = ['stock', 'limit_per_day']
    success_url = '/'  # not used

    def __init__(self, **kwargs):
        self.old_limit_per_day = None
        self.old_stock = None
        super(SellerUpdateStockView, self).__init__(**kwargs)

    # Must record old values before post. It will be changed during "is_valid" call.
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        self.old_limit_per_day = product.limit_per_day
        self.old_stock = product.stock
        return super(SellerUpdateStockView, self).post(request, *args, **kwargs)

    # Update avail_today by the change of limit_per_day and stock
    def form_valid(self, form):
        product = self.get_object()
        updated_object = form.save(commit=False)
        # First adjust avail_today by changing of limit_per_day
        delta_limit = updated_object.limit_per_day - self.old_limit_per_day
        updated_object.avail_today = updated_object.avail_today + delta_limit \
            if updated_object.avail_today + delta_limit > 0 else 0
        # Make sure avail_today is no more than stock
        updated_object.avail_today = min(updated_object.avail_today, updated_object.stock)
        # Then, if stock increased, we increase avail_today if still have quota
        delta_stock = updated_object.stock - self.old_stock
        quota = updated_object.limit_per_day - product.avail_today - product.pending_order - product.ordered_today
        if delta_stock > 0 and quota > 0:
            updated_object.avail_today = updated_object.avail_today + min(delta_stock, quota)
        updated_object.save()
        return HttpResponseRedirect(self.get_success_url())


class SellerUpdateProductView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    template_name = 'mainapp/seller_update_product.html'
    fields = ['name', 'orig_price', 'discount', 'description', 'order_requirement', 'must_review',
              'review_requirement', 'amazon_link', 'how_to_find', 'stock', 'limit_per_day']

    def __init__(self, **kwargs):
        self.old_limit_per_day = None
        self.old_stock = None
        super(SellerUpdateProductView, self).__init__(**kwargs)

    # Cannot directly assign to success_url because object.id is not valid in the beginning
    def get_success_url(self):
        self.success_url = reverse('seller_product_detail', args=[self.object.id])
        return super(SellerUpdateProductView, self).get_success_url()

    # Must record old values before post. It will be changed during "is_valid" call.
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        self.old_limit_per_day = product.limit_per_day
        self.old_stock = product.stock
        return super(SellerUpdateProductView, self).post(request, *args, **kwargs)

    # Update avail_today by the change of limit_per_day and stock
    def form_valid(self, form):
        product = self.get_object()
        updated_object = form.save(commit=False)
        # First adjust avail_today by changing of limit_per_day
        delta_limit = updated_object.limit_per_day - self.old_limit_per_day
        updated_object.avail_today = updated_object.avail_today + delta_limit \
            if updated_object.avail_today + delta_limit > 0 else 0
        # Make sure avail_today is no more than stock
        updated_object.avail_today = min(updated_object.avail_today, updated_object.stock)
        # Then, if stock increased, we increase avail_today if still have quota
        delta_stock = updated_object.stock - self.old_stock
        quota = updated_object.limit_per_day - product.avail_today - product.pending_order - product.ordered_today
        if delta_stock > 0 and quota > 0:
            updated_object.avail_today = updated_object.avail_today + min(delta_stock, quota)
        updated_object.save()
        return HttpResponseRedirect(self.get_success_url())


class SellerUpdateImageView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, AjaxableResponseMixin,
                            UpdateView):
    permission_required = 'mainapp.change_product'
    model = Product
    fields = ['image']
    success_url = '/'  # not used


class SellerProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, SellerQuerySetMixin, DetailView):
    # Sellers can view their products if they can add products
    permission_required = 'mainapp.add_product'
    model = Product
    template_name = 'mainapp/seller_product_detail.html'


###################
# Buyer Views
###################
def cancel_pending_job(product_id, buyer_id):
    if product_id in pending_order_map and buyer_id in pending_order_map[product_id]:
        del pending_order_map[product_id][buyer_id]
        Product.objects.filter(id=product_id).update(
            stock=F('stock') + 1, avail_today=F('avail_today') + 1, pending_order=F('pending_order') - 1)
    return schedule.CancelJob


class BuyerProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'mainapp.view_product'

    template_name = 'mainapp/buyer_product_list.html'
    paginate_by = 2
    model = Product
    ordering = '-updated_at'


class BuyerProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'mainapp.view_product'
    model = Product
    template_name = 'mainapp/buyer_product_detail.html'


class BuyerRequestOrderView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'mainapp.add_purchase'
    model = Purchase
    fields = ['order_number', 'order_screenshot']
    template_name = 'mainapp/buyer_request_order.html'
    success_url = reverse_lazy('buyer_product_list')  # TODO: change to order status

    def get_context_data(self, **kwargs):
        kwargs['expiration'] = pending_order_map[long(self.kwargs.get('product_id'))][self.request.user.id]\
                               + EXPIRATION_TIME * 60 * 1000
        return super(BuyerRequestOrderView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        form.instance.product_id = product
        form.instance.buyer_id = self.request.user
        form.instance.status = Purchase.ORDERED_STATUS
        return super(BuyerRequestOrderView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        prev_order = Purchase.objects.filter(product_id=product, buyer_id=self.request.user)
        if not product.avail_today:
            return render(self.request, 'mainapp/buyer_request_order_error.html',
                          {'error': _(u'Oops! The deal is over. Be faster next time.')})
        elif prev_order:
            return render(self.request, 'mainapp/buyer_request_order_error.html',
                          {'error': _(u'Sorry, you can only buy a product once!')})
        else:
            # If not resuming from a pending order (typical case)
            if product.id not in pending_order_map or self.request.user.id not in pending_order_map[product.id]:
                # Update all counters.
                Product.objects.filter(id=self.kwargs.get('product_id')).update(
                    stock=F('stock') - 1, avail_today=F('avail_today') - 1, pending_order=F('pending_order') + 1)
                # Add pending order info to map and schedule a cancel job
                pending_order_map[product.id].update({self.request.user.id: time() * 1000})
                schedule.every(EXPIRATION_TIME).minutes.do(cancel_pending_job, product.id, self.request.user.id)
            return super(BuyerRequestOrderView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        if product.id not in pending_order_map or self.request.user.id not in pending_order_map[product.id]:
            return render(self.request, 'mainapp/buyer_request_order_error.html',
                          {'error': _(u'Sorry, time is over!')})
        else:
            Product.objects.filter(id=self.kwargs.get('product_id')).update(
                pending_order=F('pending_order') - 1, ordered=F('ordered') + 1, ordered_today=F('ordered_today') + 1)
            return super(BuyerRequestOrderView, self).post(request, *args, **kwargs)