from django.db import models
from django.contrib.auth.models import User

class Meat(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class BBQEvent(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('event date')
    share_link = models.CharField(max_length=200)
    available_meat = models.ManyToManyField(Meat)

class Visitor(models.Model):
    name = models.CharField(max_length=200)
    guests = models.IntegerField(default=0)
    selected_meats = models.ManyToManyField(Meat)