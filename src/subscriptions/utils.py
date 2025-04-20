# from django.db.models import Q
# from .models import UserSubscription,SubscriptionStatus
# from helper import billing

# def refresh_user_subscriptions(user_ids=None):

#      active_qs_lookup = Q(status=SubscriptionStatus.ACTIVE) | Q(status=SubscriptionStatus.TRIALING)
#      qs = UserSubscription.objects.filter(active_qs_lookup)

#      if isinstance(user_ids, list):
#           qs = qs.filter(user__id__in=user_ids)
#      elif isinstance(user_ids, int):
#           qs = qs.filter(user__id=user_ids)
#      elif isinstance(user_ids, str):
#           qs = qs.filter(user__id=user_ids)

#      completed_count = 0
#      qs_count = qs.count()     
          
#      for obj in qs:
#           if obj.stripe_id:
#                     sub_data = billing.get_subscription(obj.stripe_id , raw=False)
#                     for k,v in sub_data.items():
#                          setattr(obj , k, v)
#                     completed_count+=1     
#                     obj.save()
#      print(qs_count, completed_count,'')
#      return qs_count == completed_count      
# 
from django.db.models import Q
from .models import UserSubscription,SubscriptionStatus
from helper import billing

def refresh_user_subscriptions(user_ids=None, active_only=True, days_left=0, days_ago=0):

     qs = UserSubscription.objects.all()

     if active_only:
          qs = qs.by_user_triling()

     if user_ids is not None:
          qs = qs.by_user_ides(user_ids=user_ids)

     if days_ago > 0:
           qs = qs.by_days_ago(days_ago=days_ago)     

     if days_left > 0:
           qs = qs.by_days_left(days_left=days_left)     

     completed_count = 0
     qs_count = qs.count()     
          
     for obj in qs:
          print("Updating user", obj.user, obj.subscription, obj.current_period_end)
          if obj.stripe_id:
                    sub_data = billing.get_subscription(obj.stripe_id , raw=False)
                    for k,v in sub_data.items():
                         setattr(obj , k, v)
                    completed_count+=1     
                    obj.save()
     print(qs_count, completed_count,'')
     return qs_count == completed_count                        