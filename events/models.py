from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from simple_history.models import HistoricalRecords


from django.contrib.auth import get_user_model


# This class is an abstract class that will be inherited by all other models. It will add a uuid field
# and a created field to all models that inherit it
User = get_user_model()



class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    attendee = ArrayField(models.CharField(max_length=120, null=True, blank=True), null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='event_updated_by')
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=120, null=True, blank=True)
    invitation_sent = models.BooleanField(default=False)
    google_calendar_event_id = models.CharField(max_length=120, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        """Extra model properties."""
        ordering = ['-title']

    def __str__(self):
        return self.title