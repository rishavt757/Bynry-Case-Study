from django.db import models
from accounts.models import CustomUser

class SupportStaff(models.Model):
    DEPARTMENT_CHOICES = [
        ('Customer Service', 'Customer Service'),
        ('Technical Support', 'Technical Support'),
        ('Billing Support', 'Billing Support'),
        ('Emergency Response', 'Emergency Response'),
        ('Field Operations', 'Field Operations')
    ]

    LEVEL_CHOICES = [
        (1, 'Level 1 - First Response'),
        (2, 'Level 2 - Technical'),
        (3, 'Level 3 - Specialist'),
        (4, 'Level 4 - Manager')
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='support_staff')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    support_level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    max_active_tickets = models.IntegerField(default=5)
    current_active_tickets = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.department} (Level {self.support_level})"

    class Meta:
        verbose_name = 'Support Staff'
        verbose_name_plural = 'Support Staff'


class SupportLog(models.Model):
    ACTION_CHOICES = [
        ('Created', 'Ticket Created'),
        ('Assigned', 'Ticket Assigned'),
        ('Status Update', 'Status Updated'),
        ('Comment', 'Comment Added'),
        ('Escalated', 'Ticket Escalated'),
        ('Resolved', 'Ticket Resolved'),
        ('Reopened', 'Ticket Reopened')
    ]

    request = models.ForeignKey('requests.ServiceRequest', on_delete=models.CASCADE, related_name='support_logs')
    staff = models.ForeignKey(SupportStaff, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default='Comment')
    note = models.TextField()
    time_spent = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - Request {self.request.reference_number} by {self.staff.user.username}"

    class Meta:
        ordering = ['-created_at']
