from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^seller/add-product/$', views.SellerAddProductView.as_view(), name='seller_add_product'),
    url(r'^seller/product-list/$', views.SellerProductListView.as_view(), name='seller_product_list'),
    url(r'^seller/product-detail/(?P<pk>\d+)$', views.SellerProductDetailView.as_view(), name='seller_product_detail'),
    url(r'^seller/update-stock/(?P<pk>\d+)$', views.SellerUpdateStockView.as_view(), name='seller_update_stock'),
    url(r'^seller/update-product/(?P<pk>\d+)$', views.SellerUpdateProductView.as_view(), name='seller_update_product'),
    url(r'^seller/update-image/(?P<pk>\d+)$', views.SellerUpdateImageView.as_view(), name='seller_update_image'),
    url(r'^buyer/product-list/$', views.BuyerProductListView.as_view(), name='buyer_product_list'),
    url(r'^buyer/product-detail/(?P<pk>\d+)$', views.BuyerProductDetailView.as_view(), name='buyer_product_detail'),
    url(r'^buyer/request-order/(?P<product_id>\d+)$', views.BuyerRequestOrderView.as_view(), name='buyer_request_order'),
    url(r'^buyer/order-done/$', views.BuyerOrderDoneView.as_view(), name='buyer_order_done'),
    url(r'^buyer/order-list/$', views.BuyerOrderListView.as_view(), name='buyer_order_list'),

]