from django.shortcuts import render, redirect
import matplotlib
import requests
from .models import StockTransaction, Vehicle, House, Crypto, Stock, User, Asset, AssetType
from enum import Enum, auto
import matplotlib.pyplot as plt
from datetime import datetime
import io
import urllib, base64
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.cache import cache
from datetime import timedelta

IS_LOGGED = "isLogged"

class VIEWTYPE(Enum):
    list = auto()
    detail = auto()
    edit = auto()

# Create your views here.

def login(request):
    context = {}
    if request.method == "POST":
        if User.objects.get(username="admin").check_password(request.POST.get('password', None)):
            cache.set(IS_LOGGED, True, 86400)
            return redirect('index')
        else:
            context['msg'] = "Password is wrong!"
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')

def logout(request):
    if cache.get(IS_LOGGED, False):
        cache.delete(IS_LOGGED)
    return redirect('login')

def home(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
    context = {}
    return render(request, 'index.html', context)

def index(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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

def vehicle(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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
        asset = Asset.objects.get(category='V')
        if _method == "delete":
            Vehicle.objects.get(id=id).delete()
        else:
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
        # update asset
        targets = Vehicle.objects.all()
        asset.current_value = sum([x.purchase_price for x in targets])
        asset.save()
        return redirect('vehicle')

def house(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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
        asset = Asset.objects.get(category='R')
        if _method == "delete":
            House.objects.get(id=id).delete()
        else:
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
        # update asset
        targets = House.objects.all()
        asset.current_value = sum([x.purchase_price for x in targets])
        asset.save()
        return redirect('house')

def crypto(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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
        asset = Asset.objects.get(category='C')
        if _method == "delete":
            Crypto.objects.get(id=id).delete()
        else:
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
        # update asset
        targets = Crypto.objects.all()
        asset.current_value = sum([x.purchase_price for x in targets])
        asset.save()
        return redirect('crypto')

def stock(request):
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
    context = {}
    ticker = request.GET.get('ticker', None)
    apikey = "wW55pKJzExsThjPDizKdf8OAdDfkvLPW"
    if ticker:
        params = {
            "apiKey": apikey,
            "ticker": ticker,
        }
        response = requests.get("https://api.polygon.io/v3/reference/tickers", params=params)
        response_json = response.json()
        results = response_json["results"][0]

        context['ticker'] = results["ticker"]
        context['name'] = results["name"]
        context['market'] = results["market"].upper()
        context['currency'] = results["currency_name"].upper()
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
        elif VIEWTYPE[viewtype] is VIEWTYPE.edit:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Stock.objects.get(id=id)
            return render(request, 'stock/add.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                stock_data = Stock.objects.get(id=id)
                context['data'] = stock_data
                base_url = 'https://api.polygon.io/v2/aggs/ticker/'
                ticker = stock_data.ticker_symbol
                date_from = stock_data.purchase_date
                date_to = datetime.now().date()
                purchase_price = stock_data.purchase_price

                # Get the stock data
                url = f"{base_url}{ticker}/range/1/day/{date_from}/{date_to}"
                params = {
                    'apiKey': apikey,
                }
                response = requests.get(url, params=params)
                data = response.json()
                
                # Generate the Plot for html
                dates = [datetime.utcfromtimestamp(item['t'] / 1000).date() for item in data['results']]
                closing_prices = [item['c'] for item in data['results']]
                matplotlib.use('Agg')
                fig, ax = plt.subplots()
                ax.plot(dates, closing_prices, label=ticker)
                ax.axhline(y=purchase_price, color='r', linestyle='--', label='Purchase Price')
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                ax.set_title(f'{ticker} Stock Price')
                plt.xticks(rotation=45)
                plt.tight_layout()
                ax.legend()
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                context['plot_url'] = f'data:image/png;base64,{plot_url}'

                current_price = closing_prices[-1]
                current_total_value = stock_data.share * current_price
                purchase_total_value = stock_data.share * purchase_price
                total_return = current_total_value - purchase_total_value
                context['total_return'] = total_return

                return render(request, 'stock/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        asset = Asset.objects.get(category='E')
        if _method == "delete":
            Stock.objects.get(id=id).delete()
        else:
            share = int(request.POST.get('share', 0))
            ticker_symbol = request.POST.get('ticker_symbol', "")
            market = request.POST.get('market', "")
            currency = request.POST.get('currency', "")
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            a = Stock(
                asset_id=asset.id,
                share=share,
                ticker_symbol=ticker_symbol,
                market=market,
                currency=currency,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            if id > 0:
                a.id = id
            a.save()
        # update asset
        targets = Stock.objects.all()
        asset.current_value = sum([x.purchase_price for x in targets])
        asset.save()
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
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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
    if cache.get(IS_LOGGED, False) is not True:
        return redirect('login')
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