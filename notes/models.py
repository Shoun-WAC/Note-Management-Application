from django.db import models
from authentication.models import Profile

ACTION_CHOICES = (
    ('Created', 'Created'),
    ('Edited', 'Edited'),
    ('Deleted', 'Deleted'),
)

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag_name
    

class Notes(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_tag = models.ManyToManyField(Tag, blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notes_created')
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class NoteVersion(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    version_number = models.IntegerField()
    edited_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='note_versions')
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)#make it updated_at

    def __str__(self):
        return f"{self.note.title} - Version {self.version_number}"
    
class NoteActivityLog(models.Model):
    note_version = models.ForeignKey(NoteVersion, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(choices=ACTION_CHOICES, max_length=50)
    performed_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='note_activities')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.note.title} by {self.performed_by.user.username} at {self.timestamp}"