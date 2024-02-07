from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    context = {}
    if request.method == "POST":
        stock = request.POST.get('stock', None)
        crypto = request.POST.get('crypto', None)
        vehicle = request.POST.get('vehicle', None)
        house = request.POST.get('house', None)

        context['stock'] = stock
        context['crypto'] = crypto
        context['vehicle'] = vehicle
        context['house'] = house
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')
