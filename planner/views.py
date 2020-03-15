from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django import forms
from datetime import datetime
from django.db import IntegrityError

from .models import Visitor, BBQEvent, Meat, MeatReservation


def events_view(request):
    if request.user.is_authenticated:
        events = BBQEvent.objects.filter(organizer=request.user.id)
        for event in events:
            event.total_visitors = len(event.visitors.all())
            event.reserved_meat = {}
            for visitor in event.visitors.all():
                event.total_visitors += visitor.guests
                for meat_reservation in visitor.meat_reservations.all():
                    event.reserved_meat[meat_reservation.meat.name] = meat_reservation.quantity
        return render(request, 'planner/events.html', {
            'events': events,
        })
    else:
        return HttpResponseRedirect(reverse('planner:login'))


class NewEventForm(forms.Form):
    date = forms.DateTimeField()
    time = forms.TimeField()
    OPTIONS = ()
    for meat in Meat.objects.all():
        OPTIONS += ((meat.name, meat.name),)
    meat_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple, choices=OPTIONS)


def new_event_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = NewEventForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                time = form.cleaned_data['time']
                meat = form.cleaned_data['meat_types']
                available_meat = []
                for meat_name in meat:
                    available_meat.append(Meat.objects.get(name=meat_name))
                date = date.replace(hour=time.hour, minute=time.minute)
                event = BBQEvent(organizer=request.user, date=date)
                event.save()
                event.available_meat.set(available_meat)
                event.share_link = f'http://127.0.0.1:8000/planner/event/{event.id}'
                event.save()
                context = {
                'success_message': "Event Created!",
                'available_meat': Meat.objects.all()
                }
            template = loader.get_template('planner/new_event.html')
            return HttpResponse(template.render(context, request))
            context = {
                'error_message': "Invalid form",
                'available_meat': Meat.objects.all()
            }
            template = loader.get_template('planner/new_event.html')
            return HttpResponse(template.render(context, request))
        else:
            context = {
                'form': NewEventForm(),
                'available_meat': Meat.objects.all()
            }
            template = loader.get_template('planner/new_event.html')
            return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('planner:login'))


def get_event(request, event_id):
    event = get_object_or_404(BBQEvent, pk=event_id)
    if request.method == 'POST':
        name = request.POST['name']
        guests = request.POST['guests']
        meat_reservations = []
        for meat in event.available_meat.all():
            if request.POST[meat.name]:
                meat_reservation = MeatReservation(
                    meat=meat, quantity=int(request.POST[meat.name]))
                meat_reservation.save()
                meat_reservations.append(meat_reservation)
        visitor = Visitor(name=name, guests=guests)
        visitor.save()
        visitor.meat_reservations.set(meat_reservations)
        event.visitors.add(visitor)
        context = {
            'success_message': "Registration successful!",
            'event': event
        }
        template = loader.get_template('planner/get_event.html')
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'event': event
        }
        template = loader.get_template('planner/get_event.html')
        return HttpResponse(template.render(context, request))


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('planner:events')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'planner/login.html', {
                'error_message': "Wrong login credentials.",
            })
    else:
        template = loader.get_template('planner/login.html')
        return HttpResponse(template.render({}, request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('planner:login'))


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError as e:
            return render(request, 'planner/register.html', {
                'error_message': e.__cause__,
            })
        login(request, user)
        return redirect('planner:events')
    else:
        template = loader.get_template('planner/register.html')
        return HttpResponse(template.render({}, request))
