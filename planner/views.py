from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Visitor, BBQEvent, Meat

def events_view(request):
    if request.user.is_authenticated:
        events = BBQEvent.objects.filter(organizer=request.user.id)
        return render(request, 'planner/events.html', {
            'events': events,
        })
    else:
        return HttpResponseRedirect(reverse('planner:login'))

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return events_view(request)
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
        user = User.objects.create_user(username, email, password)

        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('planner:events'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'planner/login.html', {
                'error_message': "Wrong login credentials.",
            })
    else:
        template = loader.get_template('planner/register.html')
        return HttpResponse(template.render({}, request))
