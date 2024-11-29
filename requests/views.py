from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ServiceRequestForm
from .models import ServiceRequest

@login_required
def submit_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()
            return redirect('track_requests')
    else:
        form = ServiceRequestForm()

    return render(request, 'requests/submit_request.html', {'form': form})

@login_required
def track_requests(request):
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'requests/track_requests.html', {'requests': requests})

