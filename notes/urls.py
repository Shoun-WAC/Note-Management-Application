from django.urls import path
from .views import *

urlpatterns = [
    path('note-management', NoteCreateView.as_view(), name='note_management'),
    path('list-notes', ListNotesView.as_view(), name='list_notes'),
    path('<id>/versions/', ListNoteVersionView.as_view(), name='list_note_versions'),
    path('create-note-tag', NoteTagCreationView.as_view(), name='create_note_tag'),
    path('activity-logs', NoteActivityLogListView.as_view(), name='note_activity_logs'),
]