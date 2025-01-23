# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
from decouple import config
import stripe

DEBUG = config('DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str, default='')

if 'sk_test' not in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError('Invalid strip key')

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(name, email,meta={}):
    res = stripe.Customer.create(
  name=name,
  email=email,
  metadata=meta
)
    if res:
        return res