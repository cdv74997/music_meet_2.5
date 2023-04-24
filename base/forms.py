from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Event, Group, Musician, User, Skill, InstrumentSkill, InboxMessage, Contract, Demo, UserMusician, UserGroup
#from django.contrib.auth.models import User
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class MyUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['location','name', 'flier', 'instruments_needed', 'description', 'occurring', 'musicians_needed']
        widgets = {
           'occurring' : forms.SelectDateWidget(),
           #'occurring': forms.DateInput()#forms.SelectDateWidget(), 
           #'occuring': forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
            #'occurring': AdminDateWidget()
            #'time': forms.TimeInput(format='%H:%M'),
        }
        labels = {'location': 'Zip Code'}
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
        exclude = ['owner', 'primary']

    def __init__(self, *args, **kwargs):
        super(GenresForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    
class InstrumentsForm(ModelForm):
    class Meta:
        model = InstrumentSkill
        fields = '__all__'
        exclude = ['owner', 'primary']

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

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"
        exclude = ['owner', 'added', 'musician', 'group', 'accepted', 'event']

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class DemoForm(forms.ModelForm):
    class Meta:
        model = Demo
        fields = "__all__"
        exclude = ['owner', 'added']

    def __init__(self, *args, **kwargs):
        super(DemoForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class UserMusicianForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    class Meta:
        model = UserMusician
        fields = '__all__'
        exclude = ['id', 'musician_id', 'user', 'avatar', 'bio', 'instruments', 'genres', 'account_type']
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password","Passwords Do Not Match!")
        return cleaned_data

class UserGroupForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    class Meta:
        model = UserGroup
        fields = '__all__'
        exclude = ['id', 'group_id', 'user', 'avatar', 'bio', 'account_type', 'featured_image']
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password","Passwords Do Not Match!")
        return cleaned_data

class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['account_type']

