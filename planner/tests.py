import uuid

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import BBQEvent, Meat, MeatReservation, Visitor


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password=test_password)
        return client, user
    return make_auto_login


@pytest.mark.django_db
def test_events_redirect(client):
    url = reverse('planner:events')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_event_not_found(client):
    url = reverse('planner:get_event', kwargs={'event_id': 1})
    response = client.get(url)
    assert response.status_code == 404


@pytest.fixture
def event_date():
    return timezone.now()


@pytest.fixture
def meat_name():
    return 'Pork'


@pytest.fixture
def add_meat(auto_login_user, meat_name):
    client, user = auto_login_user()
    url = reverse('planner:add_meat')
    data = {
        'meat_name': meat_name,
    }
    client.post(url, data=data)


@pytest.mark.django_db
def test_events_authenticated(auto_login_user, add_meat, event_date):
    client, user = auto_login_user()

    add_meat
    meat = Meat.objects.all()
    event = BBQEvent(organizer=user, date=event_date)
    event.save()
    event.available_meat.set(meat)
    visitor = Visitor(name='Piet', guests=4)
    visitor.save()
    meat_reservation = MeatReservation(meat=meat[0], quantity=3)
    meat_reservation.save()
    visitor.meat_reservations.set([meat_reservation])
    event.visitors.set([visitor])

    url = reverse('planner:events')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_event_found(auto_login_user, event_date):
    client, user = auto_login_user()
    event = BBQEvent(organizer=user, date=event_date)
    event.save()
    url = reverse('planner:get_event', kwargs={'event_id': event.id})
    response = client.get(url)
    assert response.context['event'] == event
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_meat(auto_login_user, meat_name):
    client, user = auto_login_user()
    url = reverse('planner:add_meat')
    data = {
        'meat_name': meat_name,
    }
    response = client.post(url, data=data)
    assert response.context['success_message'] == 'Meat added'


@pytest.mark.django_db
def test_create_event(auto_login_user, add_meat, meat_name):
    client, user = auto_login_user()
    add_meat
    url = reverse('planner:new_event')
    data = {
        'date': '2020-03-27',
        'time': '21:00',
        'meat_types': meat_name
    }
    response = client.post(url, data=data)
    assert response.context['success_message'] == 'Event created'


@pytest.fixture
def add_event(auto_login_user, add_meat, meat_name):
    client, user = auto_login_user()
    add_meat
    url = reverse('planner:new_event')
    data = {
        'date': '2020-03-27',
        'time': '21:00',
        'meat_types': meat_name
    }
    client.post(url, data=data)


@pytest.mark.django_db
def test_register_visitor_for_event(client, add_event):
    add_event
    events = BBQEvent.objects.all()
    url = reverse('planner:get_event', kwargs={'event_id': events[0].id})
    data = {
        'name': 'Piet',
        'guests': 5,
        'Pork': 3
    }
    response = client.post(url, data=data)
    assert response.context['success_message'] == 'Registration successful'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password, error_message', [
        ('', '', 'Invalid form'),
        ('', 'password', 'Invalid form'),
        ('username', '', 'Invalid form'),
        ('username', 'password', 'Wrong login credentials')
    ]
)
def test_login_data_validation(
    username, password, error_message, client
):
    url = reverse('planner:login')
    data = {
        'username': username,
        'password': password
    }
    response = client.post(url, data=data)
    assert response.context['error_message'] == error_message


@pytest.mark.parametrize(
    'username, email, password, error_message', [
        ('', '', '', 'Invalid form'),
        ('', '', 'password', 'Invalid form'),
        ('', 'email', '', 'Invalid form'),
        ('username', '', '', 'Invalid form')
    ]
)
def test_register_data_validation(
    username, email, password, error_message, client
):
    url = reverse('planner:register')
    data = {
        'username': username,
        'email': email,
        'password': password
    }
    response = client.post(url, data=data)
    assert response.context['error_message'] == error_message


@pytest.mark.django_db
def test_register_valid_data(client):
    url = reverse('planner:register')
    data = {
        'username': 'username',
        'email': 'email@hotmail.com',
        'password': 'password'
    }
    response = client.post(url, data=data)
    assert response.status_code == 302
