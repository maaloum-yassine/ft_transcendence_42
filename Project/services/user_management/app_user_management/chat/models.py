from django.db import models
from user_managemanet.models import CustomUser 
# Create your models here.
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver} at {self.timestamp}'

class Connected(models.Model):
    connected = models.ForeignKey(CustomUser, related_name='connected', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)