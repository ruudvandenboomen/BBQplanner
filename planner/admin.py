from django.contrib import admin

from .models import BBQEvent, Meat, MeatReservation, Visitor

admin.site.register(Visitor)
admin.site.register(BBQEvent)
admin.site.register(Meat)
admin.site.register(MeatReservation)
