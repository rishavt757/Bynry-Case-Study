from django.contrib.auth.models import AbstractUser
from django.db import models
import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    if not re.match(r'^\+?\d{10,15}$', value):
        raise ValidationError(f'{value} is not a valid phone number.')

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True, validators=[validate_phone_number])
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
