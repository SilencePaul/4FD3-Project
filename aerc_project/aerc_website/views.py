from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Vehicle, User, Asset, AssetType
from enum import Enum, auto
from django.views.decorators.csrf import csrf_protect, csrf_exempt

class VIEWTYPE(Enum):
    list = auto()
    detail = auto()

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

@csrf_exempt
def vehicle(request):
    context = {}
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            total = Vehicle.objects.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = Vehicle.objects.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = page * size + len(data) != total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'vehicle/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Vehicle.objects.get(id=id)
            return render(request, 'vehicle/detail.html', context)
    if request.method == "POST":
        vehicleAsset = Asset.objects.get(category='V')
        id = int(request.POST.get('id', 0))
        brand = request.POST.get('brand', "")
        model = request.POST.get('model', "")
        year = request.POST.get('year', "")
        color = request.POST.get('color', "")
        VIN = request.POST.get('VIN', "")
        purchase_price = request.POST.get('purchase_price', "")
        purchase_date = request.POST.get('purchase_date', "")
        a = Vehicle(asset_id=vehicleAsset.id, id=id, brand=brand, model=model, year=year, color=color, VIN=VIN, purchase_price=purchase_price, purchase_date=purchase_date)
        a.save()
        return redirect('vehicle')

def user(request):
    context = {}
    if request.method == "GET":
        total = User.objects.count()
        size = int(request.GET.get('size', 20))
        page = int(request.GET.get('page', 1))
        data = User.objects.all()[(page-1)*size:page*size]
        context['total'] = total
        context['size'] = size
        context['page'] = page
        context['data'] = data
        context['hasPrev'] = page > 1
        context['hasNext'] = page * size + len(data) != total
        context['pagePrev'] = page - 1
        context['pageNext'] = page + 1
        return render(request, 'user/index.html', context)

def asset(request):
    context = {}
    if request.method == "GET":
        total = Asset.objects.count()
        size = int(request.GET.get('size', 20))
        page = int(request.GET.get('page', 1))
        data = Asset.objects.all()[(page-1)*size:page*size]
        for d in data:
            for c in AssetType.CHOICES:
                if c[0] == str(d.category):
                    d.category = c[1]
        context['total'] = total
        context['size'] = size
        context['page'] = page
        context['data'] = data
        context['hasPrev'] = page > 1
        context['hasNext'] = page * size + len(data) != total
        context['pagePrev'] = page - 1
        context['pageNext'] = page + 1
        return render(request, 'asset/index.html', context)