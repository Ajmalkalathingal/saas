from django.db import models
from django.conf import settings
import helper.billing
from allauth.account.signals import (
    user_signed_up ,
    email_confirmed
)

# Create your models here.

User = settings.AUTH_USER_MODEL # "auth.user"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(null=True,blank=True)
    conf_init_email = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}'
    
    def save(self,*args, **kwargs):
        if not self.stripe_id:
            if self.init_email and self.conf_init_email:
                email = self.init_email
                if email!='' or email is not None:
                    stripe_id = helper.billing.create_customer(email=email,metadata={
                        "user_id": self.user.id, 
                        "username": self.user.username
                    },)
                    self.stripe_id = stripe_id.id

        return super().save(*args, **kwargs)
    
    
def user_signed_up_handler(request, user,*args,**kwargs):
    email = user.email
    Customer.objects.create(user=user,init_email=email,conf_init_email=False)


user_signed_up.connect(user_signed_up_handler)

def email_confirmed_helper(request, email_address,*args,**kwargs):
    qs = Customer.objects.filter(init_email=email_address,conf_init_email=False)

    for q in qs:
        q.conf_init_email = True
        q.save()

email_confirmed.connect(email_confirmed_helper)
