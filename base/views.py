from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView
from django.db.models import Q
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .utils import searchEvents, paginateEvents
#from django.contrib.auth.forms import UserCreationForm
from .models import Event, Topic, Message, Musician, Group, User, Review, Distances, Skill, InstrumentSkill, InboxMessage, Contract, Demo
from .forms import EventForm, UserForm, MusicianForm, GroupForm, MyUserCreationForm, GenresForm, InstrumentsForm, InboxMessageForm, ContractForm, DemoForm, AccountTypeForm, UserMusicianForm, UserGroupForm
from django.core.exceptions import ObjectDoesNotExist
import logging
import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect

def go_back(request):
    # Get the previous page URL
    redirect_url = request.META.get('HTTP_REFERER')
    
    # Redirect to the previous page
    print(request.META['HTTP_REFERER'])
    return redirect(redirect_url)


logger = logging.getLogger('django')
def accountType(request): 
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        print(form_type)
        if form_type == 'musician_info':
            return redirect('musician_info_form')
        elif form_type == 'group_info':
            return redirect('group_info_form')
    else:
        return render(request, 'base/account_type.html')


def registerMusician(request):
    form = UserMusicianForm()
    if request.method == 'POST':
        form = UserMusicianForm(request.POST)
        if form.is_valid():
            try:
                # we need to grab primaryskills to create them
                primaryinstrument = form.cleaned_data['primaryinstrument'],
                primarygenre=form.cleaned_data['primarygenre'],
                user=User.objects.create(
                    email=form.cleaned_data['email'],
                    password=make_password(form.cleaned_data['password']),
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    account_type="M"
                )
                musician=Musician.objects.create(
                    user=user,
                    primaryinstrument=primaryinstrument,
                    primarygenre=primarygenre,
                    experience=form.cleaned_data['experience'],
                    location=form.cleaned_data['location'],
    
                )
                instrumentskill=InstrumentSkill.objects.create(
                    owner=user,
                    name=primaryinstrument,
                    primary=True

                )
                genre=Skill.objects.create(
                    owner=user,
                    name=primarygenre,
                    primary=True
                )

                subject = "Welcome to MusicMeet"
                message = "We are glad that you came here to find your music.\nSincerely,\nThe Music Meet Team."
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
    
                messages.success(request, 'Thank you for registering! Please sign in.')
                return redirect('login')
            except IntegrityError as e:
                if 'email' in str(e):
                    form.add_error('email', 'This email is already registered.')
                elif 'username' in str(e):
                    form.add_error('username', 'This username is already taken.')
                else:
                    messages.error(request, 'An error occurred during registration')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/musician_register.html', {'form': form})
def updateUserMusician(request):
    user=request.user
    musician=Musician.objects.get(id=user.musician.id)
    user_form = UserForm(instance=request.user)
    musician_form = MusicianForm(instance=request.user.musician)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        musician_form = MusicianForm(request.POST, request.FILES, instance=request.user.musician)

        if user_form.is_valid() and musician_form.is_valid():
            user_form.save()
            musician_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('account')
    context={'user_form': user_form, 'musician_form': musician_form}
    return render(request, 'base/musician_update.html', context)

def updateUserGroup(request):
    user=request.user
    group=Group.objects.get(id=user.group.id)
    user_form = UserForm(instance=request.user)
    group_form = GroupForm(instance=request.user.group)

    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        group_form = GroupForm(request.POST, request.FILES, instance=request.user.group)

        if user_form.is_valid() and group_form.is_valid():
            user_form.save()
            group_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('account')
    context={'user_form': user_form, 'group_form': group_form}
    return render(request, 'base/group_update.html', context)

def registerGroup(request):
    form = UserGroupForm()
    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():

            try:
                group_name = form.cleaned_data['group_name']
                user=User.objects.create(
                    email=form.cleaned_data['email'],
                    password=make_password(form.cleaned_data['password']),
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    account_type="G"
                )
                group=Group.objects.create(
                    user=user,
                    group_name=form.cleaned_data['group_name'],
                    genre=form.cleaned_data['genre'],
                    location=form.cleaned_data['location'],
    
                )
                subject = "Welcome to MusicMeet"
                message = "We are glad that your group " + group_name + " came here to find your talent.\nSincerely,\nThe Music Meet Team."
                messages.success(request, 'Thank you for registering! Please sign in.')
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                return redirect('login')
            except IntegrityError as e:
                if 'email' in str(e):
                    form.add_error('email', 'This email is already registered.')
                elif 'username' in str(e):
                    form.add_error('username', 'This username is already taken.')
                else:
                    messages.error(request, 'An error occurred during registration')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/group_register.html', {'form': form})




# Create your views here.
TEMPLATES = {
    'account_type': 'account_type.html',
    'musician_info': 'musician_info.html',
    'group_info': 'group_info.html',
}

FORMS = [
    ('account_type', AccountTypeForm),
    ('musician_info', UserMusicianForm),
    ('group_info', UserGroupForm),
]

def register_wizard_view(request):
    wizard_view = SessionWizardView.as_view(FORMS, template_name=TEMPLATES)
    return wizard_view(request)

def get_form_instance(wizard, step):
    if step == 'musician_info':
        return Musician(user=wizard.get_cleaned_data_for_step('account_type')['user'])
    if step == 'group_info':
        return Group(user=wizard.get_cleaned_data_for_step('account_type')['user'])
    return super(SessionWizardView, wizard).get_form_instance(step)

def done(wizard, form_list, **kwargs):
    user = form_list[0].save()
    if user.account_type == 'M':
        musician_info = form_list[1].save(commit=False)
        musician_info.user = user
        musician_info.save()
    else: 
        group_info = form_list[2].save(commit=False)
        group_info.user = user
        group_info.save()
    return redirect('home')
#events = [
#   {'id':1, 'name':'Banda Fest'},
#   {'id':2, 'name':'Quincenera en Los Angeles'},
#   {'id':3, 'name':'Punk Rock Night, Calabasus: The Daffys'},
#]

def musician(request, pk):
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

def groupEventSearch(request, pk):
    group = Group.objects.get(id=pk)
    print(group.user.id)
    eventsG = Event.objects.filter(host__id=group.user.id).order_by("occurring")
    print(eventsG)
    eventsG_count = eventsG.count
    messages = Message.objects.filter(user=group.user).order_by("created")
    topics = Topic.objects.all()[0:5]
    custom_range, eventsG, paginator = paginateEvents(request, eventsG, 8)
    message_dict = {}
    groupeventsearching = "yes"
    for event in eventsG:
        message_dict[event] = len(messages.filter(event__id=event.id))
    context = {'eventsG': eventsG, 'eventsG_count': eventsG_count,'messages': messages, 'message_dict': message_dict, 'topics': topics, 'custom_range': custom_range,
    'paginator': paginator, 'group': group, 'groupeventsearching': groupeventsearching}
    

    return render(request, 'base/home.html', context)


@login_required(login_url="login")
def home(request):
    distanceChoices = Distances.objects.all()
    
    events, topics, event_count, event_messages, message_dict, q, now, distance = searchEvents(request)
    custom_range, events, paginator = paginateEvents(request, events, 3)
    unread_messages = InboxMessage.objects.filter(recipient=request.user, is_read=False)
    eventsearching = "yes"
    
    
    
    # Create an object containing the groups object, musicians object, etc.:
    context = {'events': events, 'topics': topics, 'unread_count': unread_messages.count(),
     'event_count': event_count, 'event_messages': event_messages, 'message_dict': message_dict,
     'q': q, 'paginator': paginator, 'custom_range': custom_range, 'eventsearching': eventsearching, 'now': now, 'distance': distance,'distanceChoices': distanceChoices}

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
    #participants = event.participants.all()
    # Make a query to all users that have accepted a contract for this event
    contracts = Contract.objects.filter(event=event, accepted=True)
    musicians = Musician.objects.filter(contract__in=contracts)
    participants = User.objects.filter(musician__in=musicians)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        message = Message.objects.create(
            user = request.user, 
            event = event,
            body = body
        )
        groupUser = event.host
        subject = str(event.name) + " Notification. " + str(request.user.first_name) + " " + str(request.user.last_name) + " commented on your event."
        sysUser = User.objects.get(username='MusicMeet')
        inboxMessage = InboxMessage.objects.create(
            sender=sysUser,
            recipient=groupUser,
            name=groupUser.first_name + " " + groupUser.last_name,
            subject = subject,
            body = body,
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
        primarygenre = request.POST.get('primarygenre')
        primaryinstrument=request.POST.get('primaryinstrument')
        #musician = form.save(commit=False)
       # musician.user = request.user
        Musician.objects.create(
            user=request.user,
            primaryinstrument=primaryinstrument,
            primarygenre=primarygenre,
            experience=request.POST.get('experience'),
            location=request.POST.get('location'),
            demo=request.POST.get('demo')
        )

        Skill.objects.create(
            owner=request.user,
            name=primarygenre,
            primary=True
        )
        InstrumentSkill.objects.create(
            owner=request.user,
            name=primaryinstrument,
            primary=True
        )
        
        user = request.user
        subject = 'Welcome to MusicMeet'
        message = 'We are glad to help you utilize your talent!'
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
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
        
        primaryinstrument = request.POST.get('primaryinstrument')
        primarygenre = request.POST.get('primarygenre')
        instrument = InstrumentSkill.objects.get(Q(owner=request.user) & Q(primary=True))
        instrument.name = primaryinstrument
        instrument.save()
        genre = Skill.objects.get(Q(owner=request.user) & Q(primary=True))
        genre.name = primarygenre
        genre.save()
        musician.primaryinstrument = primaryinstrument
        musician.primarygenre = primarygenre
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
        topic_name = group.genre
        topic, created = Topic.objects.get_or_create(name=topic_name)
        if form.is_valid():
            event = form.save(commit=False)
            print(event.occurring)

            #If the event has not passed already it will create the event 
            if(event.occurring >= datetime.date.today()):
                print('Date has not passed yet');
                #Create the event 
                Event.objects.create(
                    host=request.user,
                    topic=topic,
                    name=request.POST.get('name'),
                    instruments_needed=request.POST.get('instruments_needed'),
                    flier=request.FILES.get('flier'),
                    description=request.POST.get('description'),
                    occurring=event.occurring,
                    location = request.POST.get('location'),
            
                )
                return redirect('home')
            #If the date has already passed it will not create the event 
            else:
                print('Date has already passed');
                messages.error(request,"Enter a date that has not passed");
            #Do not allow user to create event if the date has already passed 
        
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
        
        topic_name = Topic.objects.get(name=request.POST.get('topic'))
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
            event.musicians_needed = request.POST.get('musicians_needed')
            if (event.musicians_needed == 0):
                event.booked = True
            else:
                event.booked = False
        
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
def deleteDemo(request, pk):
    demo = Demo.objects.get(id=pk)

    if request.user != demo.owner:
        return HttpResponse('You are not authorized here!!')

    if request.method == 'POST':
        demo.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': event})



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
        else:
            messages.error(request, 'form not valid')
    
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
    if hasattr(user, 'group'):
        group_name = user.group.group_name
        genre = user.group.genre
        location = user.group.location
        events = Event.objects.filter(host__id=user.id)
        context = {'group_name': group_name, 'genre': genre, 'location': location, 'events': events, 'user': user}
        return render(request, 'base/group_account.html', context)
    else:
        now = datetime.date.today()
        # I need to collect every group that I have an event that has passed for which I have accepted for
        contracts = Contract.objects.filter(musician__id = user.musician.id, accepted=True)
        contract_ids = [contract.contract_id for contract in contracts]
        # performed is past tense so occurring must be in the past
        events = Event.objects.filter(contract__contract_id__in=contract_ids, occurring__lt=now)
        event_ids = [event.id for event in events]
        groups = Group.objects.filter(contract__event_id__in=event_ids)
        genres = user.skill_set.all()
        instruments = user.instrumentskill_set.all()
        demos = user.demo_set.all()
        context = {'user': user, 'genres': genres, 'instruments': instruments, 'demos': demos, 'groups': groups}
        return render(request, 'base/musician_account.html', context)

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
            if genre.primary:
                Musician.objects.filter(id=user.musician.id).update(primarygenre=form.cleaned_data.get("name"))

            
            form.save()
            messages.success(request, 'Genre was revised successfully')
            return redirect('account')

    context = {'form': form}
    return render(request, 'base/genre_form.html', context)

@login_required(login_url='login')
def deleteGenre(request, pk):
    user = request.user
    genre = user.skill_set.get(id=pk)
    if request.method == "POST":
        if genre.primary:
            messages.error(request, "You are not allowed to delete your primary Genre!")

        else:
            genre.delete()
            messages.success(request, "Genre was successfully deleted!")
        return redirect('account')
    context = {'obj': genre}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def addDemo(request):
    user = request.user
    form = DemoForm()

    if request.method == 'POST':
        form = DemoForm(request.POST, request.FILES)
        title=request.POST.get('title')

        demovid=request.FILES.get('demovid')
        print(title)
        if form.is_valid():
            demo = form.save(commit=False)
            Demo.objects.create(
                owner=user,
                title=title,
                demovid=demovid,
            )
            messages.success(request, 'Demo was added successfully!')
            return redirect('account')
        
            

    context = {'form': form}
    return render(request, 'base/demo.html', context)


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
            if instrument.primary:
                Musician.objects.filter(id=user.musician.id).update(primaryinstrument=form.cleaned_data.get("name"))

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
        if instrument.primary:
            messages.error(request, "You are not allowed to delete your primary instrument!")
        else:
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
            if hasattr(recipient, 'group'):
                return redirect('view-group', pk=recipient.group.id)
            elif hasattr(recipient, 'musician'):
                return redirect('view-musician', pk=recipient.musician.id)
            else:
                return redirect('user-profile', pk=recipient.id)
    context = {'recipient': recipient, 'form': form}
    
    return render(request, 'base/message_form.html', context)

@login_required(login_url="login")
def viewReviews(request):
    reviews = Review.objects.filter(musician=request.user.musician).order_by('-created_at').first()
    context = {'reviews': reviews}
    return render(request, 'base/ratings.html', context)

@login_required(login_url="login")
def createContract(request, pk):
    musician = Musician.objects.get(id=pk)
    user = request.user
    group = user.group
    eventsToStart = Event.objects.filter(Q(host=user) & Q(musicians_needed__gte=1))
    events = Event.objects.filter(host=user, booked=False)
    #for event in eventsToStart:
    #    id = event.id
    #    # Asks the question does a contract exist for this user
    #    reject = Contract.objects.filter(Q(event__id=id) & Q(musician__id=musician.id))
    #    print(not reject)
    #    if not reject:
    #        events |= Event.objects.filter(id=id)
    
    formC = ContractForm(user)

    
    if request.method == "POST":
        formC = ContractForm(user,request.POST)
    
        eventC = request.POST.get('eventC')
        reject = Contract.objects.filter(Q(event__name=eventC) & Q(musician__id=musician.id))
        if not reject:
            print("clear")
        else:
            messages.error(request, "You cannot send multiple contracts to a musician for the same event")
            return redirect("home")

        #eventId = event.id
        #eventsub = Event.objects.get(name=eventC)
        if formC.is_valid():
            contract = formC.save(commit=False)
            contract.musician = musician
            contract.group = user.group
            
            contract.save()
            messagebody = "Hello, " + str(musician) + " you have a new contract offer from " + str(user.group) + ".\n" + "Please respond fill out your response here. Thank you.\n" + "Sincerely,\n" + "The MusicMeet Team"
            messagebodyEmail = "Hello, " + str(musician) + " you have a new contract offer from " + str(user.group) + ".\n" + "Please respond by viewing the notification for this offer in your inbox in the app. Thank you.\n" + "Sincerely,\n" + "The MusicMeet Team"
            subject = "Music Meet Contract Offer. Offer ID: " + str(contract.contract_id)
            sysUser = User.objects.get(username='MusicMeet')
            groupmessageSubject = "Music Meet Offer Sent. Offer ID: " + str(contract.contract_id)
            groupmessagebody = "Hello, " + str(user) + " this message confirms that you have sent " + str(musician) + " a contract offer to perform as a " + str(contract.instrument) + " for the venue " + str(contract.event.name) + "\nPlease allow some time for a response. Thank you.\n" + "Sincerely,\n" + "The MusicMeet Team"
            groupmessagebodyemail = "Hello, " + str(user) + " this email confirms that you have sent " + str(musician) + " a contract offer to perform as a " + str(contract.instrument) + " for the venue " + str(contract.event.name) + "\nPlease allow some time for a response. Thank you.\n" + "Sincerely,\n" + "The MusicMeet Team"
            InboxMessage.objects.create(
                sender=sysUser,
                recipient=musician.user,
                name=musician.user.first_name + " " + musician.user.last_name,
                subject = subject,
                body = messagebody,
                contract_related = True,
                contract_id = contract.contract_id,

            )
            InboxMessage.objects.create(
                sender=sysUser,
                recipient=user,
                name=user.first_name + " " + user.last_name,
                subject = groupmessageSubject,
                body = groupmessagebody,
                contract_related = False,
                contract_id = contract.contract_id,

            )
            send_mail(
                subject,
                messagebodyEmail,
                settings.EMAIL_HOST_USER,
                [musician.user.email],
                fail_silently=False,
            )
            send_mail(
                groupmessageSubject,
                groupmessagebodyemail,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Your contract was sent successfully')
            return redirect('home')
        else:
            messages.error(request, "Your contract returned an error!")
    context = {'events': events, 'formC': formC}
    return render(request, 'base/contract-create.html', context)

@login_required(login_url="login")
def reviewContract(request, pk):
    user = request.user
    message = user.inboxmessages.get(id=pk)
    contract_id = message.contract_id
    contract = Contract.objects.get(contract_id=contract_id)
    context = {'contract': contract, 'message': message}
    return render(request, 'base/contract-review.html', context)

@login_required(login_url="login")
def rejectContract(request, pk):
    user = request.user
    contract = Contract.objects.get(contract_id=pk)
    contract.delete()
    musicianmessagesubject = "Offer ID:" + str(contract.contract_id) + " Termination Confirmation"
    musicianmessagebody = "Hello, " + str(user) + ".\n" + "This message confirms that you have rejected the offer made by " + str(contract.group) + ". " + "Thank you.\n" + "Sincerely,\n" + "The MusicMeet Team"
    groupmessageSubject = "Offer ID: " + str(contract.contract_id) + " Rejected"
    groupmessagebody = "Hello, " + str(contract.group) + ".\n" + "This notice confirms that " + str(user) + " has rejected your contract offer. The offer is terminated. Thank you. \nSincerely,\nThe MusicMeet Team"  
    sysUser = User.objects.get(username='MusicMeet')
    InboxMessage.objects.create(
        sender=sysUser,
        recipient=musician.user,
        name=contract.group.user.first_name + " " + contract.group.user.last_name,
        subject = subject,
        body = messagebody,
        contract_related = False,
        contract_id = contract.contract_id
    )
    InboxMessage.objects.create(
        sender=sysUser,
        recipient=user,
        name=contract.group.user.first_name + " " + contract.group.user.last_name,
        subject = groupmessageSubject,
        body = groupmessagebody,
        contract_related = False,
        contract_id = contract.contract_id
    )
    send_mail(
        subject,
        messagebodyEmail,
        settings.EMAIL_HOST_USER,
        [musician.user.email],
        fail_silently=False,
    )
    send_mail(
        groupmessageSubject,
        groupmessagebodyemail,
        settings.EMAIL_HOST_USER,
        [contract.group.user.email],
        fail_silently=False,
    )
    return render(request, 'contract-deleted.html')

@login_required(login_url="login")
def acceptContract(request, pk):
    user = request.user
    message = InboxMessage.objects.get(id=pk)
    contract_id = message.contract_id
    contract = Contract.objects.get(contract_id=contract_id)
    contract.accepted = True
    # Once the contract is accepted the message will still exist but never be able to be reviewed again
    # Which reminds me of the need to implement delete inbox message
    message.contract_related = False
    # Decrement the musicians wanted from the event
    event = contract.event

    num = event.musicians_needed
    if (num == 0):
        messages.error(request, "This event is already booked! Offer no longer valid.")
        contract.delete()
        return redirect('home')
    newnum = num - 1
    event.musicians_needed = newnum
    if (newnum == 0):
        event.booked = True
    event.save()
    contract.save()
    message.save()
    subject = "Confirmation For Contract With " + str(contract.group.group_name) + " For Venue " + str(contract.event.name) + " Contract ID: " + str(contract.contract_id)
    messagebodyEmail = "This email is to confirm that you, " + str(user.first_name) + " " + str(user.last_name) + " have agreed to perform with " + str(contract.group.group_name) + " on the day of " + str(contract.event.occurring) + " at " + str(contract.start_time) + " until " + str(contract.end_time) + " for a rate of $" + str(contract.pay) + " per hour.\n" + "The event will be held at " + str(contract.location) + ".\n" + " Please make note of the terms in this binding agreement outlined here. " + str(contract.description)
    messagebody = "This message is to confirm that you, " + str(user.first_name) + " " + str(user.last_name) + " have agreed to perform with " + str(contract.group.group_name) + " on the day of " + str(contract.event.occurring) + " at " + str(contract.start_time) + " until " + str(contract.end_time) + " for a rate of $" + str(contract.pay) + " per hour.\n" + "The event will be held at " + str(contract.location) + ".\n" + " Please make note of the terms in this binding agreement outlined here. " + str(contract.description)
    groupmessageSubject = "Confirmation of Contract Acceptance For " + str(user.first_name) + " " + str(user.last_name) + " For Venue " + str(contract.event.name) + " Contract ID: " + str(contract.contract_id)
    groupmessagebodyEmail = "This email confirms that "+ str(user.first_name) + " " + str(user.last_name) + " has accepted your offer."
    groupmessagebody = "This message confirms that "+ str(user.first_name) + " " + str(user.last_name) + " has accepted your offer."
    sysUser = User.objects.get(username='MusicMeet')
    InboxMessage.objects.create(
        sender=sysUser,
        recipient=user,
        name=contract.group.user.first_name + " " + contract.group.user.last_name,
        subject = subject,
        body = messagebody,
        contract_related = False,
        contract_id = contract.contract_id
    )
    InboxMessage.objects.create(
        sender=sysUser,
        recipient=contract.group.user,
        name=user.first_name + " " + user.last_name,
        subject = groupmessageSubject,
        body = groupmessagebody,
        contract_related = False,
        contract_id = contract.contract_id
    )
    send_mail(
        subject,
        messagebodyEmail,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    send_mail(
        subject,
        groupmessagebodyEmail,
        settings.EMAIL_HOST_USER,
        [contract.group.user.email],
        fail_silently=False,
    )
    context = {'contract': contract}
    return render(request, 'base/contract-accept.html', context)



def viewMusician(request, pk):
    musician = Musician.objects.get(id=pk)
    demos = Demo.objects.filter(owner__id=musician.user.id)
    # We will only have one primary instrument
   
    # The complement of the set containing exclusively primary instrument
    instruments = InstrumentSkill.objects.filter(owner=musician.user)
   
    genres = Skill.objects.filter(owner=musician.user)
    contractable = False
    user = request.user
    try:
        if user.group.exists():
            events = Event.objects.filter(Q(host=user) & Q(booked=False))
            if events.exists:
                 contractable = True
    except:
        contractable = False
    
    context = {'musician': musician, 'contractable': contractable, 'instruments': instruments,'genres': genres, 'demos': demos}
    return render(request, 'base/musician.html', context)

def viewGroup(request, pk):
    group = Group.objects.get(id=pk)
    # Lets just have it to see all their events
    events = Event.objects.filter(host=group.user)
    context = {'group': group, 'events': events}
    return render(request, 'base/group.html', context)

@login_required(login_url="login")
def pastEvents(request):
    now = datetime.date.today()
    if hasattr(user, 'group'):
        events = Events.objects.filter(host=group.user, occurring__lt=now)
    elif hasattr(user, 'musician'):
        musician = user.musician
        # in both subsets of past and future events we are using accepted contracts as query
        # here we must check if date occurring on event has passed
        contracts = Contracts.objects.filter(musician__id=musician.id, accepted=True, event__occurring__lt=now)
        contract_ids = [contract.contract_id for contract in contracts]
        events = Events.objects.filter(contract__contract_id__in=contract_ids)
        # This is the tricky part we must see if an accepted contract exists with this musician
    context = {'events': events}
    return(request, 'base/events-past.html')
# This is  a comment

@login_required(login_url="login")
def currentEvents(request):
    now = datetime.date.today()
    if hasattr(user, 'group'):
        events = Events.objects.filter(host=group.user, occurring__gte=now)
    elif hasattr(user, 'musician'):
        musician = user.musician
        # in both subsets of past and future events we are using accepted contracts as query
        # here we must check if date occurring on event has passed
        contracts = Contracts.objects.filter(musician__id=musician.id, accepted=True, event__occurring__gte=now)
        contract_ids = [contract.contract_id for contract in contracts]
        events = Events.objects.filter(contract__contract_id__in=contract_ids)
        # This is the tricky part we must see if an accepted contract exists with this musician
    else:
        return redirect('login')
    context = {'events': events}
    return(request, 'base/events-current.html')
