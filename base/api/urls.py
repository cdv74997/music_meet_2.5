from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('events/', views.getEvents),
    path('events/<str:pk>/', views.getEvent),
]