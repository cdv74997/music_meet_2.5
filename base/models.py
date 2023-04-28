from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
#from django.contrib.auth.models import User
import uuid
from embed_video.fields import EmbedVideoField


ACCOUNT_TYPES = (
    ('M', 'Musician'),
    ('G', 'Group'),
)




class User(AbstractUser):
    
    username = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    account_type = models.CharField(default='M', max_length = 10, choices = ACCOUNT_TYPES)
    #musician_Account = models.BooleanField(default=False, null=True)
    #group_Account = models.BooleanField(default=False, null=True)
    email = models.EmailField(unique=True, null=True)
    
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return str(self.first_name) + str(self.last_name) 


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.name)




class Event(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    flier = models.ImageField(null=True, blank=True, default="flyer.png")
    instruments_needed = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    musicians_needed = models.PositiveIntegerField(default=1)
    booked = models.BooleanField(default=False)
    # many to many relationship
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    occurring = models.DateField(null=True)
    #time = models.TimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length = 50)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
 
    class Meta:
        # this is default for main view but group view should order by occurring
        ordering = ['-updated', '-created']
        unique_together = (('name', 'host'),)

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # this is a one to many relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        ordering = ['-updated', '-created']



    def __str__(self):
        return self.body[0:50]

    
experience_choices = (
    ('One Year','0-1'),
    ('Two To Three Years','2-3'),
    ('Four To Seven Years','4-7'),
    ('Eight Or More Years','8+'),
)

class Skill(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    primary = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.name)

class InstrumentSkill(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    primary = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.name)

class Musician(models.Model):
    # username, primary key, charfield,  max length of 60
    #uname = models.CharField(max_length = 60, primary_key = True) #fk???
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # instruments, charfield, max length of 200
    primaryinstrument = models.CharField(max_length = 200, null=True, blank=True)

    primarygenre = models.CharField(max_length = 200, null=True, blank=True)

    instruments = models.ManyToManyField(InstrumentSkill, blank=True)

    # genres, charfield, max length of 200
    genres = models.ManyToManyField(Skill, blank=True)

    # experience, floatfield, no max length?
    experience = models.CharField(default='One Year',max_length = 19, choices = experience_choices)

    #location, charField, max length of 50
    location = models.CharField(max_length = 50)

    #demo, url field, max lenght of 200, will be a url to the demo?

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    def __str__(self):
        return str(self.user.first_name + " " + self.user.last_name)


class Group(models.Model):
    #username, charfield, max length of 60, primary key
    #uname = models.CharField(max_length = 60, primary_key = True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    #group name, charfield, max length of 60
    group_name = models.CharField(max_length = 60)

    #genre, charfield, max length of 30
    genre = models.CharField(max_length = 30)

    #location, charfield, max length of 30
    location = models.CharField(max_length = 30)

    featured_image = models.ImageField(null=True, default="avatar.svg")
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    def __str__(self):
        return str(self.group_name)
    

class Contract(models.Model):
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete = models.CASCADE, null = True, blank = True)

    #unique id for each contract
    contract_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    description = models.TextField(max_length = 50000)
    instrument = models.CharField(max_length = 30)

    start_time = models.CharField(max_length = 10, default='TBD')
    end_time = models.CharField(max_length = 10, default='TBD')
    location = models.CharField(max_length =100, default='TBD')
    pay = models.DecimalField(max_digits=7, decimal_places=2, default='15.00')
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
         return self.musician.user.first_name + "'s Contract"

class InboxMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="inboxmessages")
    name = models.CharField(max_length=200, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False, null=True)
    contract_related = models.BooleanField(default=False, null=True)
    contract_id = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return f"From: {self.sender} To: {self.recipient} at {self.created}"

    class Meta:
        ordering = ['-created']

 

class Review(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE)
    comment = models.TextField(max_length=250)
    rate = models.IntegerField(default=0, validators=[
        MaxValueValidator(5),
        MinValueValidator(0),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)

class ReviewChoices(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    __empty__ = 'Unknown'

class Distances(models.Model):
    distance = models.IntegerField(default=1)
    label = models.CharField(max_length=20)

    def __str__(self):
        return str(self.label)

class Demo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_column="name")
    added = models.DateTimeField(auto_now_add=True)
    
    #video=models.FileField(upload_to="video/%y")
    demovid=models.FileField(upload_to="video/%y")
    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['-added']

class UserMusician(models.Model):
    
    
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    account_type = models.CharField(default='M', max_length = 10, choices = ACCOUNT_TYPES)
    #musician_Account = models.BooleanField(default=False, null=True)
    #group_Account = models.BooleanField(default=False, null=True)
    email = models.EmailField(unique=True, null=True)
    
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # instruments, charfield, max length of 200
    primaryinstrument = models.CharField(max_length = 200, null=True, blank=True)

    primarygenre = models.CharField(max_length = 200, null=True, blank=True)

    instruments = models.ManyToManyField(InstrumentSkill, blank=True)

    # genres, charfield, max length of 200
    genres = models.ManyToManyField(Skill, blank=True)

    # experience, floatfield, no max length?
    experience = models.CharField(default='One Year',max_length = 19, choices = experience_choices)

    #location, charField, max length of 50
    location = models.CharField(max_length = 50)

    #demo, url field, max lenght of 200, will be a url to the demo?
    
    musician_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

class UserGroup(models.Model):
    
    
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    account_type = models.CharField(default='M', max_length = 10, choices = ACCOUNT_TYPES)
    #musician_Account = models.BooleanField(default=False, null=True)
    #group_Account = models.BooleanField(default=False, null=True)
    email = models.EmailField(unique=True, null=True)
    
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    #group name, charfield, max length of 60
    group_name = models.CharField(max_length = 60)

    #genre, charfield, max length of 30
    genre = models.CharField(max_length = 30)

    #location, charfield, max length of 30
    location = models.CharField(max_length = 30)

    featured_image = models.ImageField(null=True, default="avatar.svg")
    group_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    