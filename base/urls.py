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
    path('inbox/', views.inbox, name="inbox"),
    path('message/<str:pk>/', views.viewInboxMessage, name="message"),
    path('send-message/<str:pk>/', views.createInboxMessage, name="create-message"),
    path('add-genre/', views.addGenre, name="add-genre"),
    path('add-instrument/', views.addInstrument, name="add-instrument"),
    path('update-instrument/<str:pk>/', views.updateInstrument, name="update-instrument"),
    path('delete-instrument/<str:pk>/', views.deleteInstrument, name="delete-instrument"),
    path('update-genre/<str:pk>/', views.updateGenre, name="update-genre"),
    path('delete-genre/<str:pk>/', views.deleteGenre, name="delete-genre"),
    path('view-reviews/', views.viewReviews, name="view-reviews"),
    path('group-events/<str:pk>/', views.groupEventSearch, name='group-events'),
    path('create-contract/<str:pk>/', views.createContract, name='create-contract'),
    path('review-contract/<str:pk>/', views.reviewContract, name='review-contract'),
    path('accept-contract/<str:pk>/', views.acceptContract, name='accept-contract'),
    path('decline-contract/<str:pk>/', views.rejectContract, name='decline-contract'),
    path('musician/<str:pk>/', views.viewMusician, name='view-musician'), 

]