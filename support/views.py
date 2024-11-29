from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import SupportStaff, SupportLog
from requests.models import ServiceRequest

@login_required
def dashboard(request):
    """Support staff dashboard view"""
    # Get the status counts for the statistics
    status_counts = {
        'pending': ServiceRequest.objects.filter(status='Pending').count(),
        'assigned': ServiceRequest.objects.filter(status='Assigned').count(),
        'in_progress': ServiceRequest.objects.filter(status='In Progress').count(),
        'on_hold': ServiceRequest.objects.filter(status='On Hold').count(),
        'resolved': ServiceRequest.objects.filter(status='Resolved').count(),
        'closed': ServiceRequest.objects.filter(status='Closed').count(),
        'total': ServiceRequest.objects.count()
    }

    if request.user.is_superuser:
        # Superusers can see all requests
        pending_requests = ServiceRequest.objects.filter(status='Pending').select_related('user')
        assigned_requests = ServiceRequest.objects.filter(status='Assigned').select_related('user')
        in_progress_requests = ServiceRequest.objects.filter(status='In Progress').select_related('user')
        on_hold_requests = ServiceRequest.objects.filter(status='On Hold').select_related('user')
        resolved_requests = ServiceRequest.objects.filter(status='Resolved').select_related('user')
        closed_requests = ServiceRequest.objects.filter(status='Closed').select_related('user')
    else:
        if not hasattr(request.user, 'support_staff'):
            messages.error(request, 'You do not have access to the support dashboard.')
            return redirect('home')

        staff = request.user.support_staff
        department = staff.department

        # Filter requests based on staff department and level
        department_requests = ServiceRequest.objects.filter(category__in=get_department_categories(department))
        
        pending_requests = department_requests.filter(status='Pending').select_related('user')
        assigned_requests = department_requests.filter(status='Assigned').select_related('user')
        in_progress_requests = department_requests.filter(status='In Progress').select_related('user')
        on_hold_requests = department_requests.filter(status='On Hold').select_related('user')
        resolved_requests = department_requests.filter(status='Resolved').select_related('user')
        closed_requests = department_requests.filter(status='Closed').select_related('user')

    context = {
        'status_counts': status_counts,
        'pending_requests': pending_requests,
        'assigned_requests': assigned_requests,
        'in_progress_requests': in_progress_requests,
        'on_hold_requests': on_hold_requests,
        'resolved_requests': resolved_requests,
        'closed_requests': closed_requests,
    }

    return render(request, 'support/dashboard.html', context)

@login_required
def update_request_status(request, request_id):
    """Update the status of a service request"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    # Check if user has permission to update this request
    if not request.user.is_superuser and (
        not hasattr(request.user, 'support_staff') or
        service_request.category not in get_department_categories(request.user.support_staff.department)
    ):
        messages.error(request, 'You do not have permission to update this request.')
        return redirect('support:dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        time_spent = request.POST.get('time_spent', 0)

        if new_status:
            old_status = service_request.status
            service_request.status = new_status
            
            # Update timestamps based on status
            if new_status == 'In Progress' and old_status == 'Pending':
                service_request.started_at = timezone.now()
            elif new_status == 'Resolved':
                service_request.completed_at = timezone.now()
            
            service_request.save()

            # Create support log
            try:
                # For superusers, create or get a special system staff account
                if request.user.is_superuser:
                    staff, _ = SupportStaff.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'department': 'System Administration',
                            'support_level': 3
                        }
                    )
                else:
                    staff = request.user.support_staff

                SupportLog.objects.create(
                    request=service_request,
                    staff=staff,
                    action='Status Update',
                    note=f"Status changed from {old_status} to {new_status}. {note}",
                    time_spent=timedelta(minutes=int(time_spent)) if time_spent else None
                )
                messages.success(request, f'Request status updated to {new_status}')
            except Exception as e:
                messages.error(request, f'Error creating log: {str(e)}')

        return redirect('support:dashboard')

    return render(request, 'support/update_status.html', {
        'service_request': service_request,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })

def get_department_categories(department):
    """Map department to relevant request categories"""
    category_mapping = {
        'Customer Service': ['Billing Issue', 'Other'],
        'Technical Support': ['Gas Leak', 'Maintenance'],
        'Billing Support': ['Billing Issue'],
        'Emergency Response': ['Gas Leak'],
        'Field Operations': ['New Connection', 'Maintenance'],
        'System Administration': ['Billing Issue', 'Gas Leak', 'Maintenance', 'New Connection', 'Other']  # System admins can handle all categories
    }
    return category_mapping.get(department, [])
