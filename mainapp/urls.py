from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^seller/add-product/$', views.SellerAddProductView.as_view(), name='seller_add_product'),
    url(r'^seller/product-list/$', views.SellerProductListView.as_view(), name='seller_product_list'),
    url(r'^seller/product-detail/(?P<pk>\d+)$', views.SellerProductDetailView.as_view(), name='seller_product_detail'),
    url(r'^seller/update-stock/(?P<pk>\d+)$', views.SellerUpdateStockView.as_view(), name='seller_update_stock'),
    url(r'^seller/update-product/(?P<pk>\d+)$', views.SellerUpdateProductView.as_view(), name='seller_update_product'),
]