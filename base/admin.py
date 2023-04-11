from django.contrib import admin

# Register your models here.


from .models import Event, Topic, Message, Contract, Group, Musician, User, Skill, InstrumentSkill, Review, Distances, InboxMessage

admin.site.register(Event)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Contract)
admin.site.register(Group)
admin.site.register(Musician)
admin.site.register(User)
admin.site.register(Skill)
admin.site.register(InstrumentSkill)
admin.site.register(Review)
admin.site.register(Distances)
admin.site.register(InboxMessage)
