from django.urls import path

from . import views

app_name = 'planner'
urlpatterns = [
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('events', views.events_view, name='events'),
    path('event/new', views.new_event_view, name='new_event'),
    path('event/<int:event_id>', views.get_event, name='get_event'),
    path('meat/add', views.add_meat, name='add_meat'),
]
