from django.db import models
from django.conf import settings
from chargily_pay.entity import Checkout
#from . import mixins
import uuid


from decimal import Decimal

class Customer(models.Model):
   name = models.CharField(max_length=255)
   email = models.EmailField()
   phone = models.CharField(max_length=20, blank=True, null=True)

   def __str__(self):
      return f"{self.name} ({self.email})"


class AmountCheckout(models.Model):
   class PAYMENT_STATUS(models.TextChoices):
      PENDING = "PENDING", "Pending"
      PAID = "PAID", "Paid"
      FAILED = "FAILED", "Failed"
      CANCELED = "CANCELED", "Canceled"
      EXPIRED = "EXPIRED", "Expired"

   class PAYMENT_METHOD(models.TextChoices):
      EDAHABIA = "edahabia", "edahabia"
      CIB = "cib", "cib"

   class LOCALE(models.TextChoices):
      ENGLISH = "en", "English"
      ARABIC = "ar", "Arabic"
      FRENCH = "fr", "French"

   amount = models.IntegerField()
   entity_id = models.CharField(max_length=100, unique=True)
   payment_method = models.CharField(
      max_length=10, choices=PAYMENT_METHOD.choices, default=PAYMENT_METHOD.EDAHABIA
   )
   customer = models.ForeignKey(
      Customer, on_delete=models.CASCADE, null=True, blank=True
   )
   description = models.TextField(null=True, blank=True)
   locale = models.CharField(max_length=2, choices=LOCALE.choices, default=LOCALE.FRENCH)
   status = models.CharField(
      max_length=10, choices=PAYMENT_STATUS.choices, default=PAYMENT_STATUS.PENDING
   )
   checkout_url = models.URLField()

   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   def on_paid(self):
      self.status = self.PAYMENT_STATUS.PAID
      self.save()

   def on_failure(self):
      self.status = self.PAYMENT_STATUS.FAILED
      self.save()

   def on_cancel(self):
      self.status = self.PAYMENT_STATUS.CANCELED
      self.save()

   def on_expire(self):
      self.status = self.PAYMENT_STATUS.EXPIRED
      self.save()

   def to_entity(self) -> Checkout:

      if not self.customer:
         raise ValueError("Customer is required before creating checkout.")
      entity = {
         "amount": int(self.amount) if isinstance(self.amount, Decimal) else self.amount,
         "currency": "dzd",
         "success_url": getattr(settings, "CHARGILY_SUCCESS_URL", None),
         "failure_url": getattr(settings, "CHARGILY_FAILURE_URL", None),
         "webhook_endpoint": getattr(settings, "CHARGILY_WEBHOOK_URL", None),
         "payment_method": getattr(self, "payment_method", None),
         "customer_id": getattr(settings , "CHARGILY_CUSTOMER_ID", None),
         "description": self.description or "",
         "locale": getattr(self, "locale", None),
         "pass_fees_to_customer": False,
      }
      entity = {k: v for k, v in entity.items() if v is not None}
      return Checkout(**entity)   



class Product(models.Model):
   name = models.CharField(max_length=200)
   description = models.TextField(blank=True, null=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)  # DZD
   image = models.ImageField(upload_to="products/", blank=True, null=True)

   def __str__(self):
      return self.name
