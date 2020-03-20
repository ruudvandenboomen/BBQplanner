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
def test_events_authenticated(client, auto_login_user):
    client, user = auto_login_user()
    url = reverse('planner:events')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_event_not_found(client):
    url = reverse('planner:get_event', kwargs={'event_id': 1})
    response = client.get(url)
    assert response.status_code == 404


@pytest.fixture
def event_date():
    return timezone.now()


@pytest.mark.django_db
def test_event_found(auto_login_user, event_date):
    client, user = auto_login_user()
    event = BBQEvent(organizer=user, date=event_date)
    event.save()
    url = reverse('planner:get_event', kwargs={'event_id': 1})
    response = client.get(url)
    assert response.context['event'] == event
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_meat(auto_login_user):
    client, user = auto_login_user()
    url = reverse('planner:add_meat')
    data = {
        'meat_name': 'Pork',
    }
    response = client.post(url, data=data)
    assert response.context['success_message'] == 'Meat added'


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
