from django.contrib import admin
from .models import ServiceRequest

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_customer_username', 'get_customer_email', 'description', 'status', 'created_at']

    def get_customer_username(self, obj):
        return obj.user.username
    get_customer_username.short_description = 'Customer'

    def get_customer_email(self, obj):
        return obj.user.email  # You can use other fields like `contact_number` or `address`
    get_customer_email.short_description = 'Customer Email'


admin.site.register(ServiceRequest, ServiceRequestAdmin)
