from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^seller/add-product/$', views.SellerAddProductView.as_view(), name='seller_add_product'),
    url(r'^seller/product-list/$', views.SellerProductListView.as_view(), name='seller_product_list'),
]