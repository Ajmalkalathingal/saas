from django.shortcuts import render,redirect
from django.urls import reverse
from .models import SubscriptionPrice,UserSubscription
from helper import billing
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user = request.user)

    if request.method == "POST":
        if user_sub_obj.stripe_id:
            sub_data = billing.get_subscription(user_sub_obj.stripe_id , raw=False)
            for k,v in sub_data.items():
                setattr(user_sub_obj , k, v)
            user_sub_obj.save()
            print(sub_data)
        return redirect(user_sub_obj.get_absolute_url())      

    return render(request, 'subscriptions/user_details_view.html' ,{'sub_data':user_sub_obj} )

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

