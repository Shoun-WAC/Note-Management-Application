from django.db import models
from django.contrib.auth.models import User


USER_TYPES = (
        ('Admin','Admin'),
        ('Editor','Editor'),
        ('Viewer','Viewer'),
    )

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    user_type = models.CharField(max_length=150,choices=USER_TYPES, null=True)
    is_active = models.BooleanField(default=True)