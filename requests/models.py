from django.db import models
from accounts.models import CustomUser
import uuid

class ServiceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]
    
    CATEGORY_CHOICES = [
        ('Gas Leak', 'Gas Leak'),
        ('Billing Issue', 'Billing Issue'),
        ('New Connection', 'New Connection'),
        ('Maintenance', 'Maintenance'),
        ('Other', 'Other')
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('On Hold', 'On Hold'),
        ('Issue Resolved', 'Issue Resolved'),
        ('Closed', 'Closed')
    ]

    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]

    # Core fields
    reference_number = models.CharField(max_length=10, unique=True, editable=False, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_requests')
    service_type = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    is_emergency = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Status and tracking
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    sla_breach = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)

    # Feedback
    customer_feedback = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f'SR{str(uuid.uuid4().int)[:8]}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} - {self.category} ({self.status})"

    class Meta:
        ordering = ['-created_at']
