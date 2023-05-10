from rest_framework.fields import CharField,ListField
from rest_framework.serializers import ModelSerializer
from events.models import Event

class EventSerializer(ModelSerializer[Event]):
    attendee = ListField(child=CharField(required=False), required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'start_at', 'end_at', 'location', 'attendee',)
        extra_kwargs = {'attendee': {'required': False, "allow_null": True}}



