from django.core.management.base import BaseCommand
from subscriptions.models import Subscription,UserSubscription
from customers.models import Customer
from helper import billing
from subscriptions.utils import refresh_user_subscriptions



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--days_left", default=0, type=int)
        parser.add_argument("--days_ago", default=0, type=int)
        parser.add_argument("--clear-dangling", action="store_true", default=False)
        
    def handle(self, *args, **options):

        days_left = options.get('days_left')
        days_ago = options.get('days_ago')
        clear_dangling = options.get("clear_dangling")
        
        if clear_dangling:
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
                print(existing_user_sub)
        else:
            print("Sync active subs")
            done = refresh_user_subscriptions(
                active_only=True, 
                days_left=days_left,
                days_ago=days_ago,
                # day_start=day_start,
                # day_end=day_end,
                # verbose=True
                )
            if done:
                print("Done")        