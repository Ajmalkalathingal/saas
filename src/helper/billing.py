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
    

def start_checkout_session(customer_id='',success_url='',cancel_url='',price_stripe_id=''):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
        )  
    if response:
        return response    


def get_checkout_session(strip_id):
    response = stripe.checkout.Session.retrieve(
        strip_id
        )
    return response

def get_subscription(strip_id):
    response = stripe.Subscription.retrieve(
        strip_id
    )
    return response

def get_checkout_customer_plan(session_id):
    checkout_redirect = get_checkout_session(session_id)

    customer_id = checkout_redirect.customer
    subscription_strip_id = checkout_redirect.subscription

    subscription = get_subscription(subscription_strip_id)
    return customer_id, subscription.plan.id    