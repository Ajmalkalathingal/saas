from django.core.management.base import BaseCommand
from subscriptions.models import Subscription,UserSubscription
from customers.models import Customer
from helper import billing



class Command(BaseCommand):
    def handle(self, *args, **options):
        
        qs = Customer.objects.filter(stripe_id__isnull=False)

        for customer_obj in qs:
            user = customer_obj.user
            customer_strip_id = customer_obj.stripe_id
            subs = billing.get_customer_active_subscription(customer_obj.stripe_id)

            for sub in subs:
                existing_user_sub = UserSubscription.objects.filter(stripe_id=f"{sub.id}".strip())
                if existing_user_sub.exists():
                    continue
                billing.cencel_subscription(sub.id,reason='Dangling ctive subscriptions', cancel_at_period_end=False)
                

            print(existing_user_sub.exists())