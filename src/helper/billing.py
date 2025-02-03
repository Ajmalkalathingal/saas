# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
from decouple import config
import stripe

DEBUG = config('DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str, default='')

if 'sk_test' not in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError('Invalid strip key')

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(email,metadata={}):
    res = stripe.Customer.create(
  email=email,
  metadata=metadata
)
    if res:
        return res
    

def create_Product(name,metadata={}):
    res = stripe.Product.create(
        name=name,
        metadata=metadata
)
    if res:
        return res
    
def create_price(currency="usd",
                unit_amount="9999",
                interval="month",
                product=None,
                metadata={}):
    if product is None:
        return None
    res = stripe.Price.create(
            currency=currency,
            unit_amount=unit_amount,
            recurring={"interval": interval},
            product=product,    
            metadata=metadata
        )
    if res:
        return res