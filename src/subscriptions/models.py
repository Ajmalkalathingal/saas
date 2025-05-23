from django.db import models
import helper.billing
from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings 
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError


User = settings.AUTH_USER_MODEL # "auth.User"

ALLOW_CUSTOM_GROUPS = True
SUBSCRIPTION_PERMISSIONS = [
    ("advanced", "Advanced Perm"), # subscriptions.advanced
    ("pro", "Pro Perm"),  # subscriptions.pro
    ("basic", "Basic Perm"),  # subscriptions.basic,
    ("basic_ai", "Basic AI Perm")
]    

# Create your models here.
class Subscription(models.Model):
    """
    Subscription Plan = Stripe Product
    """
    name = models.CharField(max_length=120)
    subtitle = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group) # one-to-one
    permissions =  models.ManyToManyField(Permission, limit_choices_to={
        "content_type__app_label": "subscriptions", "codename__in": [x[0]for x in SUBSCRIPTION_PERMISSIONS]
        }
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text='Ordering on Django pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Django pricing page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    feature = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        ordering =  ordering = ['order', 'featured', '-updated']


    def get_features_as_list(self):
        if not self.feature:
            return []
        return  [x.strip() for x in self.feature.split('\n')]    

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        if not self.stripe_id:
            stripe_id = helper.billing.create_Product(
                name=self.name,
                metadata={
                    "subscription__id": self.id,
                },
            )
            self.stripe_id = stripe_id.id
        
        # Save again to update the stripe_id
        super().save(*args, **kwargs)
 

# Create your models here.
class SubscriptionPrice(models.Model):
    """
    Subscription price = Stripe Product
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY = 'month', 'Monthly'
        YEARLY = 'year', 'Yearly'

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120,default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text='Ordering on Django pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Django pricing page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['subscription__order', 'order', 'featured', '-updated']
   
    def get_checkout_url(self):
        return reverse('sub-price-checkout', kwargs={'price_id' : self.id})

    @property
    def display_sub_name(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.name
    
    @property
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_as_list()
    
    @property
    def stripe_currency(self):
        return 'usd'
    
    @property
    def stripe_price(self):
        return int(self.price * 100)
    
    @property
    def product_stripe_id(self):
        return self.subscription.stripe_id if self.subscription else None

    def save(self, *args, **kwargs):
        if not self.stripe_id and self.product_stripe_id:
            print(f"Creating Stripe price for product: {self.product_stripe_id}") 
            stripe_price_response = helper.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={"subscription_plan_price_id": str(self.id)}
            )

            print(f"Stripe API Response: {stripe_price_response}") 

            if stripe_price_response and hasattr(stripe_price_response, "id"):
                self.stripe_id = stripe_price_response.id
            else:
                raise ValidationError("Failed to create Stripe price.")

        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)

class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    TRIALING = 'trialing', 'Trialing'
    INCOMPLETE = 'incomplete', 'Incomplete'
    INCOMPLETE_EXPIRED = 'incomplete_expired', 'Incomplete Expired'
    PAST_DUE = 'past_due', 'Past Due'
    CANCELED = 'canceled', 'Canceled'
    UNPAID = 'unpaid', 'Unpaid'
    PAUSED = 'paused', 'Paused'


class UserSubscriptionQueryset(models.QuerySet):

    def by_days_left(self,days_left=20):
        now = timezone.now()
        in_n_days = now + datetime.timedelta(days=days_left)
        day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, minute=59, microsecond=59)

        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end
        )
    def by_days_ago(self,days_ago=3):
        now = timezone.now()
        in_n_days = now - datetime.timedelta(days=days_ago)
        day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, minute=59, microsecond=59)

        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end
        ) 

    def by_user_triling(self):
        active_qs_lookup = Q(status=SubscriptionStatus.ACTIVE) | Q(status=SubscriptionStatus.TRIALING)
        return self.filter(active_qs_lookup)

    def by_user_ides(self,user_ids=None):
        qs = self
        if isinstance(user_ids, list):
            qs = qs.filter(user__id__in=user_ids)
        elif isinstance(user_ids, int):
            qs = qs.filter(user__id=user_ids)
        elif isinstance(user_ids, str):
            qs = qs.filter(user__id=user_ids)
        return qs     
    

class UserSubscriptionManager(models.Manager):
    
    def get_queryset(self):
        return UserSubscriptionQueryset(self.model, using=self._db)
    
class UserSubscription(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    user_cancelled = models.BooleanField(default=False)
    original_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    current_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    current_period_end = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=SubscriptionStatus.choices , null=True, blank=True)
    objects = UserSubscriptionManager()


    @property
    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name
    
    @property
    def is_active_status(self):
        return self.status in [SubscriptionStatus.ACTIVE,SubscriptionStatus.TRIALING]
    
    def serialize(self):
        return {
            'plan_name' : self.plan_name,
            'current_period_start': self.current_period_start,
            'current_period_end' : self.current_period_end,
            'status' : self.status
            }

    def get_absolute_url(self):
        return reverse('user-subscription')
    
    
    def get_cancel_url(self):
        return reverse('user-subscription-cancel')

    def save(self, *args ,**kwargs):
        if self.original_period_start is None and self.current_period_start is not None:
            self.original_period_start = self.current_period_start
        return super().save( *args ,**kwargs)


def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        # groups_ids = groups.values_list('id', flat=True) # [1, 2, 3] 
        current_groups = user.groups.all().values_list('id', flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_group_ids)


post_save.connect(user_sub_post_save, sender=UserSubscription)