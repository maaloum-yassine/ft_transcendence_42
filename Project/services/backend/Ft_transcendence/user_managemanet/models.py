from django.db import models , IntegrityError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)  # Pseudo unique et obligatoire
    email = models.EmailField(unique=True)  # Email unique et obligatoire
    first_name = models.CharField(max_length=150, null=False )
    last_name = models.CharField(max_length=150, null=False)
    avatar = models.CharField(max_length=255, default='avatars/default_avatar.png', blank=True)
    code_otp = models.CharField(max_length=64, null=True)
    is_email_verified = models.BooleanField(default=False, null=True)
    active_2fa = models.BooleanField(default=False, null=True)
    is_logged_2fa = models.BooleanField(default=False, null=True)
    is_online = models.BooleanField(default=False, null=True)
    password_reset_token_expires_at = models.DateTimeField(null=True, blank=True)


    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    def __str__(self):
        return self.username
    def set_password_reset_token_expiration(self):
        self.password_reset_token_expires_at = timezone.now() + timedelta(minutes=20)


class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocked_relationships',
        help_text="The user who initiated the block"
    )

    def __str__(self):
        return f"Friendship from {self.user} to {self.friend} - Accepted: {self.accepted}"
