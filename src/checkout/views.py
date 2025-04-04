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
    chack_out_data = billing.get_checkout_customer_plan(session_id)


    customer_id = chack_out_data.pop('customer_id') 
    subscription_price_id = chack_out_data.pop('subscription_plan_id')
    subscription_strip_id = chack_out_data.pop('subscription_strip_id')
    subscrption_data = {** chack_out_data}

    print(subscrption_data)
    try:
       sub_obj = Subscription.objects.get(subscriptionprice__stripe_id = subscription_price_id) 
       
    except :
        sub_obj = None

    try:
       user_obj = USer.objects.get(customer__stripe_id = customer_id) 
    except :
        user_obj = None

    _user_sub_exist = False 

    update_sub_options = {
        'subscription': sub_obj,
        'stripe_id' : subscription_strip_id,
        'user_cancelled' : False,
        **subscrption_data

    }    

    try:
       _user_sub_obj = UserSubscription.objects.get(user = user_obj)
       _user_sub_exist = True
    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(user = user_obj, **update_sub_options)
    except:
        _user_sub_obj = None    
        
    if None in [sub_obj,user_obj,_user_sub_obj]:
        return HttpResponseBadRequest('there was an error in your account. please contact us')

    if _user_sub_exist:

        # cencel old sub
        _old_sub_id = _user_sub_obj.stripe_id
        same_strip_id = subscription_strip_id == _old_sub_id

        print(_old_sub_id, same_strip_id, _user_sub_obj.stripe_id)

        if _old_sub_id is not None and not same_strip_id:
           
            try:
                billing.cencel_subscription(_old_sub_id, reason='Auto ended new membership', feedback='other')
            except:
                pass

        # assign new sub
        for k,v in update_sub_options.items():
            setattr(_user_sub_obj, k, v)
        _user_sub_obj.save()    

    context = {
        # 'checkout' : checkout_redirect,
    }

    return render(request, 'checkout/success.html',context)



