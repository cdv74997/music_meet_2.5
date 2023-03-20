# this is going to consist of classes that take a certian
# model that we want to serialize or object and will turn it 
# into JSON data and then we can return it
# so the serializer will work alot like the model form we are 
from rest_framework.serializers import ModelSerializer
from base.models import Event

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'