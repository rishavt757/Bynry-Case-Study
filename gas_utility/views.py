from django.shortcuts import render

def home(request):
    """
    Home page view that shows an overview of the gas utility service portal
    """
    return render(request, 'gas_utility/home.html')
