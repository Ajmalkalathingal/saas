from django.shortcuts import render
from django.urls import reverse
from .models import SubscriptionPrice

# Create your views here.

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

