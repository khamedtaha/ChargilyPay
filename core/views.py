from django.shortcuts import render , get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.http import HttpResponse, JsonResponse, HttpRequest
from chargily_pay.entity import Checkout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator  
from .services import client , create_checkout
from .models import AmountCheckout , Product , Customer
import uuid
import json



def main_test(request):
      return HttpResponse("This is a test page for Chargily payment integration.")




@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class WebhookView(View):
   checkout_model = AmountCheckout

   def post(self, request: HttpRequest, *args, **kwargs):

      signature = request.headers.get("signature")
      payload = request.body.decode("utf-8")
      if not signature:
            return HttpResponse(status=400)

      if not client.validate_signature(signature, payload):
            return HttpResponse(status=403)

      event = json.loads(payload)
      checkout_id = event["data"]["id"]
      checkout = self.checkout_model.objects.get(entity_id=checkout_id)

      checkout_status = event["type"]
      if checkout_status == "checkout.paid":
            checkout.on_paid()
      elif checkout_status == "checkout.failed":
            checkout.on_failure()
      elif checkout_status == "checkout.canceled":
            checkout.on_cancel()
      elif checkout_status == "checkout.expired":
            checkout.on_expire()
      else:
            return HttpResponse(status=400)

      return JsonResponse({}, status=200)





def payment_success(request):
   return render(request, "core/success.html")

def product_list(request):
   products = Product.objects.all()
   return render(request, "core/products.html", {"products": products})



def buy_product(request, product_id):
   product = get_object_or_404(Product, id=product_id)

   customer = Customer.objects.create(
      name="khamed",
      email="khamedkh@gmail.com",
      phone="0555555585"
   )

   checkout = AmountCheckout.objects.create(
      entity_id= str(uuid.uuid4()),
      customer=customer,
      amount=product.price,
      payment_method="edahabia",
      description=f"Pay Product : {product.name}",
      locale=AmountCheckout.LOCALE.ARABIC,
   )

   checkout = create_checkout(checkout)  

   return redirect(checkout.checkout_url)  