from django.contrib import admin
from .models import Coupon, Driver, Ride, User


admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Ride)
admin.site.register(Coupon)
