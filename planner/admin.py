from django.contrib import admin

from .models import Visitor, BBQEvent, Meat, MeatReservation

admin.site.register(Visitor)
admin.site.register(BBQEvent)
admin.site.register(Meat)
admin.site.register(MeatReservation)
