from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SupportStaff

@receiver(post_save, sender=get_user_model())
def create_support_staff_for_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        SupportStaff.objects.create(user=instance)

