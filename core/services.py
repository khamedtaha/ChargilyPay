# services.py

from chargily_pay import ChargilyClient
from django.conf import settings
from . import models

client : ChargilyClient = ChargilyClient(
   secret=settings.CHARGILY_SECRET,
   key=settings.CHARGILY_KEY,
   url=settings.CHARGILY_URL,
)

def create_checkout(checkout: models.Checkout) -> models.Checkout:
   try:
      response = client.create_checkout(checkout=checkout.to_entity())
      checkout.entity_id = response["id"]
      checkout.checkout_url = response["checkout_url"] 
      checkout.save()
      return checkout
   except Exception as e:
      checkout.status = models.AmountCheckout.PAYMENT_STATUS.FAILED
      checkout.save()
      raise