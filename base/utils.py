from .models import Event, Musician, Group, Topic, Message, User
from django.db.models import Q 
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import pgeocode
#Calculated distances based on US zip codes
dist = pgeocode.GeoDistance('US')

#Seperates events into page numbers
def paginateEvents(request, events, results):

    page = request.GET.get('page')

    paginator = Paginator(events, results)
    try: 
        events = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        events = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)

    leftIndex = (int(page) - 4)
    if leftIndex < 1: 
        leftIndex = 1
    rightIndex = (int(page) + 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages

    custom_range = range(leftIndex, rightIndex + 1)
    return custom_range, events, paginator


def calcDistance(musZip,groupZip,maxDistance):
        #distance in kms
        kms = dist.query_postal_code(musZip, groupZip)

        #Convert distance to miles
        distance = kms * .621371

        if distance < maxDistance:
            return True


def searchEvents(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    try:
        musician = request.user.musician
        genre = musician.genres
        instruments = musician.instruments
        musicianZip = musician.location
        maxDistance = 50

        # Retrieve all events that match the current user's genre and preferred instruments:
        events = Event.objects.filter(
            (Q(topic__name__icontains=genre) |
            Q(name__icontains=genre) |
            Q(description__icontains=instruments) |
            Q(instruments_needed__icontains=instruments)) & 
            Q(occurring__gte=datetime.date.today())
        )

        #Events filtered by distance
        disfilteredEvents = []

        # #Filer events based on their distance from the musician
        for event in events:
            eventZip = event.location
            if (calcDistance(musicianZip, eventZip, maxDistance)):
                disfilteredEvents.append(event)
        if disfilteredEvents:
            events = disfilteredEvents
        


        # Retrieve all messages for the above events:
        event_messages = Message.objects.filter(Q(event__topic__name__icontains=genre))

        # HttpRequest.GET = method (GET or POST). A dictionary-like object containing all given HTTP GET parameters. Returns QueryDict.
        # QueryDict.get(key) = returns value given key.
        q = request.GET.get('q') if request.GET.get('q') != None else ''
        if request.GET.get('q') != None: 
            events = Event.objects.filter(
            (Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)) & Q(occurring__gte=datetime.date.today())
            )
            event_messages = Message.objects.filter(Q(event__topic__name__icontains=q))
        
        # What this is is a query for our events
        

        musicians = Musician.objects.filter(
        #User__matches=User.objects.get(first_name__icontains=q) |
        #User__matches=User.objects.get(last_name__icontains=q) |
        #Q(User__matches=User.objects.get(first_name__icontains=q)) |
        #Q(User__matches=User.objects.get(last_name__icontains=q)) |
            Q(instruments__icontains=q) |
            Q(genres__icontains=q) |
            Q(location__icontains=q)
        )
        usersM = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ) 
        for userM in usersM:
            userMusicians = Musician.objects.filter(
                Q(user=userM)
            )
        #for userMusician in userMusicians:
            musicians |= userMusicians
        now = datetime.date.today()
        groups = Group.objects.filter(
            Q(group_name__icontains=q) |
            Q(genre__icontains=q) |
            Q(location__icontains=q)
        )
        usersG = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
        for userG in usersG:
            userGroups = Group.objects.filter(
                Q(user=userG)
            )
        
            groups |= userGroups

    except AttributeError:
        # this is how our search is extracted from what is passed to url
        q = request.GET.get('q') if request.GET.get('q') != None else ''
        # What this is is a query for our events
        events = Event.objects.filter(
            (Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)) & Q(occurring__gte=datetime.date.today())
        )
        event_messages = Message.objects.filter(Q(event__topic__name__icontains=q))
        now = datetime.date.today()
        musicians = Musician.objects.filter(
            Q(instruments__icontains=q) |
            Q(genres__icontains=q) |
            Q(location__icontains=q)
        )
        usersM = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
        for userM in usersM:
            userMusicians = Musician.objects.filter(
                Q(user=userM)
            )
        #for userMusician in userMusicians:
            musicians |= userMusicians

        groups = Group.objects.filter(
            Q(group_name__icontains=q) |
            Q(genre__icontains=q) |
            Q(location__icontains=q)
        )
        usersG = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
        for userG in usersG:
            userGroups = Group.objects.filter(
                Q(user=userG)
            )
            groups |= userGroups
    
    topics = Topic.objects.all()[0:5]
    event_count = events.count
    # Filtering down by the event topic name

    messages = Message.objects.all()
    message_dict = {}
    for event in events:
        message_dict[event] = len(messages.filter(event_id=event.id))
    
    return groups, musicians, events, topics, event_count, event_messages, message_dict, q, now

