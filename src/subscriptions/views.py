from django.shortcuts import render,redirect
from django.urls import reverse
from .models import SubscriptionPrice,UserSubscription
from helper import billing
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import utils
# Create your views here.

@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user = request.user)
    print(user_sub_obj)

    if request.method == "POST":
        finished_refresh = utils.refresh_user_subscriptions(user_ids=request.user.id, active_only=False)
        if finished_refresh:
            messages.success(request, '..................................refreshed ...............................')
        else :
            messages.warning(request, '..........................something went wrong please try again ...............................')    
        return redirect(user_sub_obj.get_absolute_url())      

    return render(request, 'subscriptions/user_details_view.html' ,{'sub_data':user_sub_obj} )


def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user = request.user)
    sub_data={}
    if request.method == "POST":
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = billing.cencel_subscription(user_sub_obj.stripe_id , cancel_at_period_end=True, reason='user wanted to end', feedback='other', raw=False)
            for k,v in sub_data.items():
                setattr(user_sub_obj , k, v)
            user_sub_obj.save()
        messages.success(request , 'your plan has been cancel')
        return redirect(user_sub_obj.get_absolute_url())      
    print(sub_data)
    return render(request, 'subscriptions/user_cancel_view.html' ,{'sub_data':user_sub_obj} )


def subscription_price_view(request,interval = 'month'):
    qs = SubscriptionPrice.objects.filter(featured=True)

    inv_mo = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoices.YEARLY

    url_path = 'pricing-intervel'
    mo_url = reverse(url_path ,kwargs={'interval' : inv_mo})
    yr_url = reverse(url_path ,kwargs={'interval' : inv_yr})

    obj_lis = qs.filter(interval=inv_mo)
    
    active = inv_mo

    if interval == inv_yr:
        obj_lis = qs.filter(interval=inv_yr)
        active = inv_yr
        
    return render(request,'subscriptions/pricing.html',{
        'obj_lis':obj_lis,
        'mo_url':mo_url,
        'yr_url' : yr_url,
        'active' : active,
    })

