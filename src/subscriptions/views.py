from django.shortcuts import render
from .models import SubscriptionPrice

# Create your views here.

def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    mothly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)

    return render(request,'subscriptions/pricing.html',{
        'monthly':mothly_qs,
        'yearly':yearly_qs  
    })
