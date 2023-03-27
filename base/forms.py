from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Event, Group, Musician, User, Skill, InstrumentSkill, InboxMessage
#from django.contrib.auth.models import User
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class MyUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'account_type', 'username', 'email', 'password1', 'password2']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'flier', 'instruments_needed', 'description', 'occurring']
        widgets = {
           'occurring' : forms.SelectDateWidget(),
           #'occurring': forms.DateInput()#forms.SelectDateWidget(), 
           #'occuring': forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
            #'occurring': AdminDateWidget()
            #'time': forms.TimeInput(format='%H:%M'),
        }
        # FixingEventForm 10_22_222
        #exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','first_name', 'last_name','username', 'email', 'bio']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        exclude = ['user']

class MusicianForm(ModelForm):
    class Meta:
        model = Musician
        fields = '__all__'
        exclude = ['user', 'genres', 'instruments']
        labels = {'instruments': 'primary instrument'}

class GenresForm(ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
        exclude = ['owner']

    def __init__(self, *args, **kwargs):
        super(GenresForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    
class InstrumentsForm(ModelForm):
    class Meta:
        model = InstrumentSkill
        fields = '__all__'
        exclude = ['owner']

    def __init__(self, *args, **kwargs):
        super(InstrumentsForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class InboxMessageForm(ModelForm):
    class Meta:
        model = InboxMessage 
        fields = ['subject', 'body']

    def __init__(self, *args, **kwargs):
        super(InboxMessageForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
