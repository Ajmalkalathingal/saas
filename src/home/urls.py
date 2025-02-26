"""
URL configuration for home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from visits.views import home,user_only_view,staff_only_view
from subscriptions.views import subscription_price_view,user_subscription_view
from checkout.views import product_price_redirect_view,checkout_redirect_view,checkout_finilized_view

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', home,name='home'),
    path('pricing/', subscription_price_view,name='pricing'),
    path('pricing/<str:interval>/', subscription_price_view,name='pricing-intervel'),
    path('protected-user/', user_only_view,name='user-only'),
    path('protected-staff/', staff_only_view,name='protected-staff'),

    # checkout
    path('checkout/sub/<int:price_id>', product_price_redirect_view,name='sub-price-checkout'),
    path('checkout/start', checkout_redirect_view,name='stripe-checkout-start'),
    path('checkout/success', checkout_finilized_view,name='stripe-checkout-end'),


    path('accounts/', include('allauth.urls')),
    path('accounts/billings/', user_subscription_view,name='user-subscription'),
    path('profiles/', include('profiles.urls')),

]
