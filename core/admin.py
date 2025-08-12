from django.contrib import admin
from .models import Customer, AmountCheckout, Product



admin.site.register(Customer)
admin.site.register(AmountCheckout)
admin.site.register(Product)