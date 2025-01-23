from django.db import models
from django.conf import settings
import helper.billing

# Create your models here.

User = settings.AUTH_USER_MODEL # "auth.user"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}'
    
    def save(self,*args, **kwargs):
        if not self.stripe_id:
            if self.user.email !='' or not None:
                stripe_id = helper.billing.create_customer(self.user.username,self.user.email)
                self.stripe_id = stripe_id.id

        return super().save(*args, **kwargs)