from django import forms
from django.shortcuts import get_object_or_404

from .models import BBQEvent, Meat


class NewEventForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewEventForm, self).__init__(*args, **kwargs)
        OPTIONS = ()
        for meat in Meat.objects.all():
            OPTIONS += ((meat.name, meat.name),)
        self.fields['meat_types'] = forms.MultipleChoiceField(
            widget=forms.SelectMultiple, choices=OPTIONS)
    date = forms.DateTimeField()
    time = forms.TimeField()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()


class NewMeatForm(forms.Form):
    meat_name = forms.CharField()


class RegisterEventPresenceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(RegisterEventPresenceForm, self).__init__(*args, **kwargs)
        for meat in event.available_meat.all():
            self.fields[meat.name] = forms.IntegerField()
    name = forms.CharField()
    guests = forms.IntegerField()
