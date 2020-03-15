from django.db import models
from django.contrib.auth.models import User


class Meat(models.Model):
    name = models.CharField(max_length=200)


class MeatReservation(models.Model):
    meat = models.ForeignKey(Meat, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class Visitor(models.Model):
    name = models.CharField(max_length=200)
    guests = models.IntegerField(default=0)
    meat_reservations = models.ManyToManyField(MeatReservation)


class BBQEvent(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('event date')
    share_link = models.CharField(max_length=200)
    available_meat = models.ManyToManyField(Meat)
    visitors = models.ManyToManyField(Visitor)
