from datetime import datetime

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.views import generic

from .forms import (LoginForm, NewEventForm, NewMeatForm,
                    RegisterEventPresenceForm, RegisterForm)
from .models import BBQEvent, Meat, MeatReservation, Visitor


def events_view(request):
    template = loader.get_template('planner/events.html')
    context = {}

    if request.user.is_authenticated:
        events = BBQEvent.objects.filter(organizer=request.user.id)
        for event in events:
            event.total_visitors = len(event.visitors.all())
            event.reserved_meat = {}
            for visitor in event.visitors.all():
                event.total_visitors += visitor.guests
                for meat_reservation in visitor.meat_reservations.all():
                    event.reserved_meat[meat_reservation.meat.name] = meat_reservation.quantity
        context['events'] = events
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('planner:login'))


def create_event(request, form):
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


def new_event_view(request):
    template = loader.get_template('planner/new_event.html')
    context = {
        'available_meat': Meat.objects.all()
    }

    if request.user.is_authenticated:
        form = NewEventForm(request.POST)
        if request.method == 'POST':
            if form.is_valid():
                create_event(request, form)
                context['success_message'] = "Event Created!"
            else:
                context['error_message'] = "Invalid form"
        else:
            context['form'] = form
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('planner:login'))


def add_meat(request):
    template = loader.get_template('planner/new_event.html')
    context = {
        'available_meat': Meat.objects.all()
    }

    form = NewMeatForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            meat_name = form.cleaned_data['meat_name']
            try:
                Meat.save(Meat(name=meat_name))
                context['success_message'] = "Meat added!"
            except IntegrityError as e:
                context['error_message'] = e.__cause__
    return HttpResponse(template.render(context, request))


def get_event(request, event_id):
    template = loader.get_template('planner/get_event.html')
    event = get_object_or_404(BBQEvent, pk=event_id)
    context = {
        'event': event
    }

    if request.method == 'POST':
        form = RegisterEventPresenceForm(request.POST, event=event)
        if form.is_valid():
            name = form.cleaned_data['name']
            guests = form.cleaned_data['guests']
            meat_reservations = []
            for meat in event.available_meat.all():
                if request.POST[meat.name]:
                    meat_reservation = MeatReservation(
                        meat=meat, quantity=int(form.cleaned_data[meat.name]))
                    meat_reservation.save()
                    meat_reservations.append(meat_reservation)
            visitor = Visitor(name=name, guests=guests)
            visitor.save()
            visitor.meat_reservations.set(meat_reservations)
            event.visitors.add(visitor)
            context['success_message'] = "Registration successful!"
    return HttpResponse(template.render(context, request))


def login_view(request):
    template = loader.get_template('planner/login.html')
    context = {}

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('planner:events')
        else:
            context['error_message'] = "Wrong login credentials."
    return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('planner:login'))


def register_view(request):
    template = loader.get_template('planner/register.html')
    context = {}

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.create_user(username, email, password)
            except IntegrityError as e:
                context['error_message'] = e.__cause__
                return HttpResponse(template.render(context, request))
            login(request, user)
            return redirect('planner:events')
    else:
        return HttpResponse(template.render({}, request))
