from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('slots/', views.get_available_slots, name='get_slots'),
    path('masters/', views.get_masters, name='get_masters'),
    path('services/', views.get_services, name='get_services'),
    path('submit/', views.submit_booking, name='submit'),
    path('cancel/<str:signed_token>/', views.cancel_booking, name='cancel'),
]
