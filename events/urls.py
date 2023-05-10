from django.urls.conf import path
from . import views


app_name = 'events'
urlpatterns = [
    path('create-event/', views.CreateEventView.as_view(), name="create_event"),
    path('edit-event/<uuid:event_id>/', views.EditEventView.as_view(), name='edit_event'),
    path('get-events/', views.RetrieveEventView.as_view(), name="get_events"),
    path('join-event/<uuid:event_id>/<uuid:user_id>/', views.JoinEventView.as_view(), name='join_event')
]