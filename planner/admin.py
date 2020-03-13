from django.contrib import admin

from .models import Visitor, BBQEvent, Meat

admin.site.register(Visitor)
admin.site.register(BBQEvent)
admin.site.register(Meat)
