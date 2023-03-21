from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('event/<str:pk>/', views.event, name="event"),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),

    path('create-event/', views.createEvent, name="create-event"),
    path('update-event/<str:pk>/', views.updateEvent, name="update-event"),
    path('delete-event/<str:pk>/', views.deleteEvent, name="delete-event"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    # with user update we need no id because it is logged in user
    path('update-user/', views.updateUser, name="update-user"),
    path('create-musician/', views.createMusician, name="create-musician"),
    path('update-musician/<str:pk>/', views.updateMusician, name="update-musician"),
    path('create-group/', views.createGroup, name="create-group"),
    path('update-group/<str:pk>/', views.updateGroup, name="update-group"),
    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),
    path('search-musicians/', views.searchMusician, name='search-musicians'),
    path('edit-register/<str:pk>/', views.editRegisterPage, name='edit-register'),
    path('group-event/', views.groupEvents, name='group-event'),
    path('search-group/', views.searchGroup, name='search-group'),
    path('account/', views.userAccount, name="account"), 
    path('inbox/', views.inbox, name="inbox")
]