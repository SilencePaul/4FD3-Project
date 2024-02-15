from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from .models import Vehicle, House, Crypto, Stock, User, Asset, AssetType
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
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        if _method == "delete":
            Vehicle.objects.get(id=id).delete()
        else:
            asset = Asset.objects.get(category='V')
            brand = request.POST.get('brand', "")
            model = request.POST.get('model', "")
            year = request.POST.get('year', "")
            color = request.POST.get('color', "")
            VIN = request.POST.get('VIN', "")
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            a = Vehicle(
                asset_id=asset.id,
                brand=brand,
                model=model,
                year=year,
                color=color,
                VIN=VIN,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            if id > 0:
                a.id = id
            a.save()
        return redirect('vehicle')

@csrf_exempt
def house(request):
    context = {}
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            total = House.objects.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = House.objects.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = page * size + len(data) != total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'house/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = House.objects.get(id=id)
            return render(request, 'house/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        if _method == "delete":
            House.objects.get(id=id).delete()
        else:
            asset = Asset.objects.get(category='R')
            property_type = request.POST.get('property_type', "")
            lot_width = float(request.POST.get('lot_width', 0))
            lot_depth = float(request.POST.get('lot_depth', 0))
            bedroom = int(request.POST.get('bedroom', 0))
            bathroom = int(request.POST.get('bathroom', 0))
            parking = int(request.POST.get('parking', 0))
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            a = House(
                asset_id=asset.id,
                property_type=property_type,
                lot_width=lot_width,
                lot_depth=lot_depth,
                bedroom=bedroom,
                bathroom=bathroom,
                parking=parking,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            if id > 0:
                a.id = id
            a.save()
        return redirect('house')

@csrf_exempt
def crypto(request):
    context = {}
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            total = Crypto.objects.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = Crypto.objects.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = page * size + len(data) != total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'crypto/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Crypto.objects.get(id=id)
            return render(request, 'crypto/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        if _method == "delete":
            Crypto.objects.get(id=id).delete()
        else:
            asset = Asset.objects.get(category='C')
            coin_name = request.POST.get('coin_name', "")
            amount = int(request.POST.get('amount', 0))
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            a = Crypto(
                asset_id=asset.id,
                coin_name=coin_name,
                amount=amount,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            if id > 0:
                a.id = id
            a.save()
        return redirect('crypto')

@csrf_exempt
def stock(request):
    context = {}
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            total = Stock.objects.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = Stock.objects.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = page * size + len(data) != total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'stock/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Stock.objects.get(id=id)
            return render(request, 'stock/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        if _method == "delete":
            Stock.objects.get(id=id).delete()
        else:
            asset = Asset.objects.get(category='E')
            share = int(request.POST.get('share', 0))
            symbol = request.POST.get('symbol', "")
            dividend = float(request.POST.get('dividend', 0))
            market = request.POST.get('market', "")
            currency = request.POST.get('currency', "")
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            a = Stock(
                asset_id=asset.id,
                share=share,
                symbol=symbol,
                dividend=dividend,
                market=market,
                currency=currency,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            if id > 0:
                a.id = id
            a.save()
        return redirect('stock')

def stock_search(request, stock_ticker):
    context = {}
    if request.method == "GET":
        stock_ticker = stock_ticker.upper()
        params = {
            "apiKey": "wW55pKJzExsThjPDizKdf8OAdDfkvLPW",
            "market": "stocks",
            "ticker": stock_ticker,
            "limit": 10
        }
        response = requests.get("https://api.polygon.io/v3/reference/tickers", params=params)
        response_json = response.json()
        
        response_json_results = response_json["results"]
        result_count = len(response_json_results)
        result_list = []
        if result_count == 1:
            result_list.append(response_json_results[0])
        elif result_count == 0:
            params = {
                "apiKey": "wW55pKJzExsThjPDizKdf8OAdDfkvLPW",
                "market": "stocks",
                "search": stock_ticker,
                "limit": 10
            }
            response = requests.get("https://api.polygon.io/v3/reference/tickers", params=params)
            response_json = response.json()
            response_json_results = response_json["results"]
            for result in response_json_results:
                result_list.append(result)
        context["result_count"] = result_count
        context["result_list"] = result_list
        return render(request, '_stock_verify.html', context)

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