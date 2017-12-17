from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.views.defaults import page_not_found
from . import views
admin.autodiscover()

urlpatterns = [
    # url(r'^signup/$', views.RegistrationView.as_view(), name='account_signup'),
    url(r'^signin/$', views.SignInView.as_view(), name='account_signin'),
    url(r'^signout/$', views.SignOutView.as_view(), name='account_signout'),
    url(r'^signup/seller/$', views.SellerRegistrationView.as_view(), name='account_signup_seller'),
    url(r'^signup/buyer/$', views.BuyerRegistrationView.as_view(), name='account_signup_buyer'),
    url(r'^profile/$', TemplateView.as_view(template_name='myauth/profile.html')),
    # url(r'^', include('allauth.urls')),
]