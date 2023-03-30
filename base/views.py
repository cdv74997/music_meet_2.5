from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .utils import searchEvents, paginateEvents
#from django.contrib.auth.forms import UserCreationForm
from .models import Event, Topic, Message, Musician, Group, User
from .forms import EventForm, UserForm, MusicianForm, GroupForm, MyUserCreationForm, GenresForm, InstrumentsForm, InboxMessageForm
from django.core.exceptions import ObjectDoesNotExist
import logging
import datetime
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger('django')

# Create your views here.

#events = [
#   {'id':1, 'name':'Banda Fest'},
#   {'id':2, 'name':'Quincenera en Los Angeles'},
#   {'id':3, 'name':'Punk Rock Night, Calabasus: The Daffys'},
#]

def musician(request):
    musician = Musician.objects.get(id=pk)
    musician_messages = Musician.message_set.all()

# do not call this login() because there is a default function called login that we need
def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # creates a session in the browser
            login(request, user)
            return redirect('home')
        else: 
            messages.error(request, 'Username or password does not exist')
        
    
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def editRegisterPage(request, pk):
    user = User.objects.get(id=pk)
    form = MyUserCreationForm(instance=user)

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)
            account_type = user.account_type
            user.username = user.username.lower()

            user.save()
            login(request, user)
            if (account_type == 'M'):
                return redirect('create-musician')
            elif (account_type == 'G'):
                return redirect('create-group')
            else:
                return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    return render(request, 'base/login_register.html', {'form': form})


def registerPage(request):
    #page = 'register'
    
    form = MyUserCreationForm()
    #musicForm = MusicianForm()
    #groupForm = GroupForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        #musicForm = MusicianForm(request.POST)
        #groupForm = GroupForm(request.POST)
        if form.is_valid(): #and (musicForm.is_valid() or groupForm.is_valid())):
            # commit is false because we need to access the user right away
            # if for some reason the user added and uppercase in their name or email
            # we want to make sure that that's lowercase automatically
            # we need to have access to be able to clean this data
            user = form.save(commit=False)
            #music_Account = user.musician_Account
            #group_Account = user.group_Account
            account_type = user.account_type
            user.username = user.username.lower()

            user.save()
            subject = 'Welcome to MusicMeet'
            message = 'We are glad to help you utilize your talent!'
        
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [form['email']],
                fail_silently=False,
            )
            #if musicForm.is_valid():
                #musicForm.save()
            #if groupForm.is_valid():
                #groupForm.save()
            login(request, user)
            if (account_type == 'M'):
                return redirect('create-musician')
            elif (account_type == 'G'):
                return redirect('create-group')
            else:
                return redirect('home')
            #return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})

def groupEvents(request):
    group = request.user.group
    events = Event.objects.filter(host=request.user).order_by("occurring")
    messages = Message.objects.all()
    message_dict = {}
    for event in events:
        message_dict[event] = len(messages.filter(event_id=event.id))
    context = {'events': events, 'messages': messages, 'message_dict': message_dict}

    return render(request, 'base/home.html', context)



def home(request):
    
    events, topics, event_count, event_messages, message_dict, q, now = searchEvents(request)
    custom_range, events, paginator = paginateEvents(request, events, 2)
    eventsearching = "yes"
    
    
    
    # Create an object containing the groups object, musicians object, etc.:
    context = {'events': events, 'topics': topics,
     'event_count': event_count, 'event_messages': event_messages, 'message_dict': message_dict,
     'q': q, 'paginator': paginator, 'custom_range': custom_range, 'eventsearching': eventsearching, 'now': now}

    # Load the base/home.html template, send the context object to the template, and output the HTML that is rendered by the template:
    return render(request, 'base/home.html', context)
# later on pk will be used as the primary key to query the
# database
def searchMusician(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    musicians = Musician.objects.filter(
        #User__matches=User.objects.get(first_name__icontains=q) |
        #User__matches=User.objects.get(last_name__icontains=q) |
        #Q(User__matches=User.objects.get(first_name__icontains=q)) |
        #Q(User__matches=User.objects.get(last_name__icontains=q)) |
        Q(primaryinstrument__icontains=q) |
        Q(primarygenre__icontains=q) |
        Q(location__icontains=q)
    )
    users = User.objects.filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)
    ) 
    for user in users:
        userMusicians = Musician.objects.filter(
            Q(user=user)
        )
        #for userMusician in userMusicians:
        musicians |= userMusicians
    
    eventsearching = ""
    groupsearching = ""
    musiciansearching = "yes"

    topics = Topic.objects.all()[0:5]
    context = {'musicians': musicians, 'topics': topics, 'eventsearching': eventsearching, 'groupsearching': groupsearching, 'musiciansearching': musiciansearching}
    return render(request, 'base/home.html', context)

def searchGroup(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    groups = Group.objects.filter(
        #User__matches=User.objects.get(first_name__icontains=q) |
        #User__matches=User.objects.get(last_name__icontains=q) |
        #Q(User__matches=User.objects.get(first_name__icontains=q)) |
        #Q(User__matches=User.objects.get(last_name__icontains=q)) |
        Q(group_name__icontains=q) |
        Q(genre__icontains=q) |
        Q(location__icontains=q)
    )
    users = User.objects.filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)
    ) 
    for user in users:
        userGroups = Group.objects.filter(
            Q(user=user)
        )
        #for userMusician in userMusicians:
        groups |= userGroups
    
    eventsearching = ""
    groupsearching = "yes"

    topics = Topic.objects.all()[0:5]
    context = {'topics': topics, 'eventsearching': eventsearching, 'groupsearching': groupsearching, 'groups': groups}
    return render(request, 'base/home.html', context)
def event(request, pk):
    #event = None
    #for i in events:
        #if i['id'] == int(pk):
            #event = i 
    event = Event.objects.get(id=pk)
    # We can query child objects of a specific event here
    # if we take the parent model (Event) to get all the children
    # all we have to get is the model name and put it in lowercase
    # says give us the entire set of messages related to this specific event
    event_messages = event.message_set.all().order_by('-created')
    participants = event.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user, 
            event = event,
            body = request.POST.get('body')
        )
        event.participants.add(request.user)
        return redirect('event', pk=event.id)
    

    context = {
        'event': event, 
        'event_messages': event_messages, 
        'participants': participants,
        }
    return render(request, 'base/event.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    events = user.event_set.all()
    event_messages = user.message_set.all()
    topics = Topic.objects.all()
    message_dict = {}
    if user.account_type=="M":
        musician = Musician.objects.get(user_id=pk)
    context = {'user': user, 'events': events, 'event_messages': event_messages, 'topics': topics, 'message_dict': message_dict}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createGroup(request):
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        Group.objects.create(
            user=request.user,
            group_name=request.POST.get('group_name'),
            genre=request.POST.get('genre'),
            location=request.POST.get('location')

        )
        return redirect('home')
    context = {'form': form}
    return render(request, 'base/create_group.html', context)

@login_required(login_url='login')
def updateGroup(request, pk):
    group = Group.objects.get(id=pk)
    form = GroupForm(instance=group)
    if request.user != group.user:
        return HttpResponse('You are not authorized here!!')

    if request.method == 'POST':
        
        group.group_name = request.POST.get('group_name')
        group.genre = request.POST.get('genre')
        group.location = request.POST.get('location')
        group.save()
        return redirect('home')
    context = {'form': form, 'group': group}
    return render(request, 'base/create_group.html', context)

@login_required(login_url='login')
def createMusician(request):
    form = MusicianForm()

    if request.method == 'POST':
        form = MusicianForm(request.POST)
        #musician = form.save(commit=False)
       # musician.user = request.user
        Musician.objects.create(
            user=request.user,
            primaryinstrument=request.POST.get('primaryinstrument'),
            primarygenre=request.POST.get('primarygenre'),
            experience=request.POST.get('experience'),
            location=request.POST.get('location'),
            demo=request.POST.get('demo')
        )
        
        user = request.user
        
        #group_Account = user.group_Account
        #if form.is_valid():
            #musician = form.save(commit=False)
            #musician.user = request.user
            #musician.save()
       
        return redirect('home')
        #return redirect('home')
        #else:
            #messages.error(request, 'an error occured during registation')
    context = {'form': form}
    return render(request, 'base/create_musician.html', context)

@login_required(login_url='login')
def updateMusician(request, pk):
    musician = Musician.objects.get(id=pk)
    form = MusicianForm(instance=musician)
    if request.user != musician.user:
        return HttpResponse('You are not authorized here!!')

    if request.method == 'POST':
        
        musician.primaryinstrument = request.POST.get('primaryinstrument')
        musician.genres = request.POST.get('genres')
        musician.experience = request.POST.get('experience')
        musician.location = request.POST.get('location')
        musician.demo = request.POST.get('demo')
        musician.save()
        return redirect('home')
    context = {'form': form, 'musician': musician}
    return render(request, 'base/create_musician.html', context)

@login_required(login_url='login')
def createEvent(request):
    user = request.user
    form = EventForm()
    group = request.user.group
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        #topic_name = Topic.objects.get(id=request.POST.get('topic'))
        topic_name = group.genre
        #topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        #event=form.save(commit=False)
        #occurring = form['occurring']
        if form.is_valid():
            event = form.save(commit=False)
            print(event.occurring)
            Event.objects.create(
                host=request.user,
                topic=topic,
            #occurring=occurring,
            #time=request.POST.get('time'),
                name=request.POST.get('name'),
                instruments_needed=request.POST.get('instruments_needed'),
                flier=request.FILES.get('flier'),
                description=request.POST.get('description'),
                occurring=event.occurring,
        
            )
            return redirect('home')
        
        
        
        
        
       # form = EventForm(request.POST)
        #if form.is_valid():
            # Step 2 in FixingEventForm 10_22_22
            #event = form.save(commit=False)
            #event.host = request.user
            #event.save()
        
    context = {'form': form, 'topics': topics}
    return render(request, 'base/event_form.html', context)

@login_required(login_url='login')
def updateEvent(request, pk):
    event = Event.objects.get(id=pk)
    #print(event.occurring)
    oldflier = event.flier
    form = EventForm(instance=event)
    topics = Topic.objects.all()
    if request.user != event.host:
        return HttpResponse('You are not authorized here!!')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        
        topic_name = Topic.objects.get(id=request.POST.get('topic'))
        #topic_name = request.POST.get('topic') only if form is like before
        topic, created = Topic.objects.get_or_create(name=topic_name)
        if form.is_valid():
            eventobj = form.save(commit=False)
            event.name = request.POST.get('name')
            #event.flier = request.FILES.get('flier')
            if (eventobj.flier == "flyer.png"):
                event.flier = oldflier
            else:
                event.flier = eventobj.flier
            
            
            print(eventobj.flier)
            event.occurring = eventobj.occurring
        
            event.topic = topic
            event.description = request.POST.get('description')
        
            event.save()
            return redirect('home')
    context = {'form': form, 'event': event, 'topics': topics}
    return render(request, 'base/event_form.html', context)

@login_required(login_url='login')
def deleteEvent(request, pk):
    event = Event.objects.get(id=pk)

    if request.user != event.host:
        return HttpResponse('You are not authorized here!!')
    
    if request.method == 'POST':
        event.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':event})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not authorized here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    
    form = UserForm(instance=user)
    try:
        musician = Musician.objects.get(user=user)
    except ObjectDoesNotExist:
        musician = None 
    try:
        group = Group.objects.get(user=user)
    except ObjectDoesNotExist:
        group = None


    #musician = Musician.objects.get(user=user)
    
    
    #musician = request.POST.get('musician')
    #group = request.POST.get('group')

    if request.method == 'POST':
        
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    context = {'form': form, 'musician': musician, 'group': group}
    return render(request, 'base/update_user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics' : topics})

def activityPage(request):
    event_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'event_messages' : event_messages})

@login_required(login_url='login')
def userAccount(request):
    user = request.user
    genres = user.skill_set.all()
    instruments = user.instrumentskill_set.all()

    context = {'user': user, 'genres': genres, 'instruments': instruments}
    return render(request, 'base/account.html', context)

@login_required(login_url='login')
def inbox(request):
    user = request.user
    messageRequests = user.inboxmessages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    return render(request, 'base/inbox.html', context)

@login_required(login_url='login')
def addGenre(request):
    user = request.user
    form = GenresForm()

    if request.method == "POST":
        form = GenresForm(request.POST)
        if form.is_valid():
            genre = form.save(commit=False)
            genre.owner = user
            genre.save()
            messages.success(request, 'Genre was added successfully!')
            return redirect('account')
    
    context = {'form': form}
    return render(request, 'base/genre_form.html', context)

@login_required(login_url='login')
def updateGenre(request, pk):
    user = request.user
    genre = user.skill_set.get(id=pk)
    form = GenresForm(instance=genre)

    if request.method == "POST":
        form = GenresForm(request.POST, instance=genre)
        if form.is_valid():
            
            form.save()
            messages.success(request, 'Genre was revised successfully')
            return redirect('account')

    context = {'form': form}
    return render(request, 'base/skill_form.html', context)

@login_required(login_url='login')
def deleteGenre(request, pk):
    user = request.user
    genre = user.skill_set.get(id=pk)
    if request.method == "POST":
        genre.delete()
        messages.success(request, "Genre was successfully deleted!")
        return redirect('account')
    context = {'obj': genre}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def addInstrument(request):
    user = request.user 
    form = InstrumentsForm()

    if request.method == "POST":
        form = InstrumentsForm(request.POST)
        if form.is_valid():
            instrument = form.save(commit=False)
            instrument.owner = user
            instrument.save()
            messages.success(request, 'Instrument was added successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'base/instrument_form.html', context)

@login_required(login_url='login')
def updateInstrument(request, pk):
    user = request.user
    instrument = user.instrumentskill_set.get(id=pk)
    form = InstrumentsForm(instance=instrument)

    if request.method == "POST":
        form = InstrumentsForm(request.POST, instance=instrument)
        if form.is_valid():

            form.save()
            messages.success(request, 'Instrument was revised successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'base/instrument_form.html', context)

@login_required(login_url='login')
def deleteInstrument(request, pk):
    user = request.user
    instrument = user.instrumentskill_set.get(id=pk)
    if request.method == "POST":
        instrument.delete()
        messages.success(request, "Instrument was successfully deleted!")
        return redirect('account')
    context = {'obj': instrument}
    return render(request, 'base/delete.html', context)
    
@login_required(login_url='login')
def viewInboxMessage(request, pk):
    user = request.user
    inboxmessage = user.inboxmessages.get(id=pk)
    if inboxmessage.is_read == False:
        inboxmessage.is_read = True
        inboxmessage.save()

    context = {'message': inboxmessage}
    return render(request, 'base/message.html', context)

@login_required(login_url='login')
def createInboxMessage(request, pk):
    recipient = User.objects.get(id=pk)
    form = InboxMessageForm()
    sender = request.user 

    if request.method == 'POST':
        form = InboxMessageForm(request.POST)
        if form.is_valid():
            inboxmessage = form.save(commit=False)
            inboxmessage.sender = sender
            inboxmessage.recipient = recipient
            inboxmessage.name = sender.first_name + " " + sender.last_name
            

            inboxmessage.save()
            messages.success(request, 'Your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id)
    context = {'recipient': recipient, 'form': form}
    return render(request, 'base/message_form.html', context)