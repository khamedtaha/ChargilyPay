from django.urls import path
from . views import main_test , WebhookView , product_list, buy_product , payment_success


urlpatterns = [
   path("webhook/", WebhookView.as_view(), name="webhook"),
   path("test/", main_test, name="main_test"),
   path("products/", product_list, name="product_list"),
   path("buy/<int:product_id>/", buy_product, name="buy_product"),
   path("success/", payment_success, name="payment_success"),
]