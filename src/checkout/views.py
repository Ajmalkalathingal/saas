from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from helper import billing
from subscriptions.models import SubscriptionPrice,Subscription,UserSubscription
from django.urls import reverse
from . import views
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest

from django.conf import settings

USer = get_user_model()

BASE_URL = settings.BASE_URL

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe-checkout-start')

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')

    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)

    except Exception as e:
        obj = None
        raise e

    if checkout_subscription_price_id is None or obj is None:
       return redirect('/pricing')
    

    customer_stripe_id = request.user.customer.stripe_id
    success_url_path = reverse("stripe-checkout-end")
    pricing_url_path = reverse("pricing")
    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url= f"{BASE_URL}{pricing_url_path}"

    price_stripe_id = obj.stripe_id

    response = billing.start_checkout_session(
        customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=price_stripe_id,
    )
    
    return redirect(response.url)

def checkout_finilized_view(request):
    session_id = request.GET.get('session_id')
    customer_id, subscription_price_id = billing.get_checkout_customer_plan(session_id)

    print(subscription_price_id)


    try:
       sub_obj = Subscription.objects.get(subscriptionprice__stripe_id = subscription_price_id) 
       
    except :
        sub_obj = None

    try:
       user_obj = USer.objects.get(customer__stripe_id = customer_id) 
    except :
        user_obj = None

    _user_sub_exist = False     

    try:
       _user_sub_obj = UserSubscription.objects.get(user = user_obj)
       _user_sub_exist = True
    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(user = user_obj, subscription=sub_obj)
    except:
        _user_sub_obj = None    
        
    if not [sub_obj,user_obj,_user_sub_obj]:
        return HttpResponseBadRequest('there was an error in your account. please contact us')

    if _user_sub_exist:
        _user_sub_obj.subscription = sub_obj
        _user_sub_obj.save()

    print(sub_obj,user_obj)
    context = {
        # 'checkout' : checkout_redirect,
        # 'subscription' : subscription
    }

    return render(request, 'checkout/success.html',context)



