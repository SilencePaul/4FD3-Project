from threading import Thread

from django.shortcuts import render, redirect
import matplotlib
import requests
from .models import CryptoTransaction, StockTransaction, Vehicle, House, Crypto, Stock, User, Asset, AssetType, LocationCategory, PropertyType, Cipher, Hasher, AssetHistory
from enum import Enum, auto
import matplotlib.pyplot as plt
from datetime import datetime
import io
import urllib, base64
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.cache import cache
from datetime import timedelta
from .schedule import setup_schedule, get_vehicles_value, get_houses_value, get_cryptos_value, get_stocks_value, update_current_values
from django.db.models import Count, Avg

setup_schedule()

USER_ID = "uid"

ALERT_COUNT = 5

class VIEWTYPE(Enum):
    list = auto()
    detail = auto()
    edit = auto()
    add = auto()
    buy_or_sell = auto()

try:
    ADMIN_ID = User.objects.get(username='admin').id
except Exception as e:
    ADMIN_ID = None

def report(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)

    context['plot_urls'] = []
    matplotlib.use('Agg')

    assets = Asset.objects.filter(user__id=uid).all()
    for a in assets:
        for c in AssetType.CHOICES:
            if c[0] == str(a.category):
                a.category = c[1]

        assetHistory = (AssetHistory.objects
                        .values('record_date')
                        .filter(asset=a)
                        .annotate(day_value=Avg('record_value'))
                        .order_by('record_date'))

        fig, ax = plt.subplots()
        record_dates = [h['record_date'] for h in assetHistory]
        day_values = [h['day_value'] for h in assetHistory]
        ax.plot(record_dates, day_values, label=a)
        ax.axhline(y=a.purchase_price, color='r', linestyle='--', label='Purchase Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title(f'{a} History Value')
        plt.xticks(rotation=45)
        plt.tight_layout()
        ax.legend()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        context['plot_urls'].append(f'data:image/png;base64,{plot_url}')

    context['assets'] = assets

    #context['assetHistory'] = assetHistory
    weighted_risk = 0
    total_value = 0
    for a in assets:
        if a.category == 'Crypto':
            weighted_risk += a.purchase_price * 3
        elif a.category == 'Stock':
            weighted_risk += a.purchase_price * 6
        elif a.category == 'Real Estate':
            weighted_risk += a.purchase_price * 9.5
        else:
            weighted_risk += a.purchase_price * 4
        total_value += a.purchase_price
        
    if total_value != 0:
        score = weighted_risk/total_value
    else:
        score = 0

    context['risk'] = score
    if score >= 9:
        context['level'] = "Low"
    elif score >= 6:
        context['level'] = "Moderate"
    elif score >= 3:
        context['level'] = "High"
    elif score >0:
        context['level'] = "Extreme"
    else:
        context['level'] = "Unknown"

    return render(request, 'report.html', context)

def register(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        passcode = request.POST.get('passcode', None)
        email = request.POST.get('email', None)
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        admin = User.objects.get(username='admin')
        if passcode == Hasher().hash(admin.checksum + datetime.now().strftime('%d/%m/%y')).encode('utf-8').hex()[:8]:
            if User.objects.filter(username=username).count() > 0:
                context['msgUsername'] = "Username invalid!"
                return render(request, 'register.html', context)
            newUser = User.objects.create_user(username, email, password, first_name=firstname, last_name=lastname)
            newUser.save()
            Asset(user=newUser, category="C").save()
            Asset(user=newUser, category="E").save()
            Asset(user=newUser, category="R").save()
            Asset(user=newUser, category="V").save()
            return redirect('login')
        else:
            context['msgPasscode'] = "Passcode invalid!"
            return render(request, 'register.html', context)
    else:
        return render(request, 'register.html')

def login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username', None)
        try:
            user = User.objects.get(username=username)
            if user.check_password(request.POST.get('password', None)):
                cache.set(user.id, True, 86400)
                res = redirect('index')
                res.set_cookie(USER_ID, value=Cipher().encrypt(str(user.id)), max_age=86400)
                return res
            else:
                context['msg'] = "Username/Password is wrong!"
                return render(request, 'login.html', context)
        except:
            context['msg'] = "Username/Password is wrong!"
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')

def logout(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    res = redirect('login')
    if cache.get(uid, False):
        cache.delete(uid)
        res.delete_cookie(USER_ID)
    return res

def home(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    context['stocks'] = Stock.objects.filter(asset__user__id=uid).all()
    context['cryptos'] = Crypto.objects.filter(asset__user__id=uid).all()
    context['vehicles'] = Vehicle.objects.filter(asset__user__id=uid).all()
    context['houses'] = House.objects.filter(asset__user__id=uid).all()

    now = datetime.now()
    weekAgo = now - timedelta(days=7)
    historyCrypto = (AssetHistory.objects
                     .filter(asset__category='C', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                     .order_by('record_date').all())
    historyStock = (AssetHistory.objects
                    .filter(asset__category='E', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                    .order_by('record_date').all())
    historyHouse = (AssetHistory.objects
                    .filter(asset__category='R', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                    .order_by('record_date').all())

    if len(historyCrypto) > 1:
        count = 0
        top = historyCrypto[0].record_value
        bottom = top
        for h in historyCrypto:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertCrypto'] = f"Crypto asset had frequent drops of {count} within the last week!"
            context['dropCrypto'] = f"Crypto asset had a maximum drop of {bottom - top:.2f}!"
    if len(historyStock) > 1:
        count = 0
        top = historyStock[0].record_value
        bottom = top
        for h in historyStock:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertStock'] = f"Stock asset had frequent drops of {count} within the last week!"
            context['dropStock'] = f"Stock asset had a maximum drop of {bottom - top:.2f}!"
    if len(historyHouse) > 1:
        count = 0
        top = historyHouse[0].record_value
        bottom = top
        for h in historyHouse:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertHouse'] = f"Real Estate asset had frequent drops of {count} within the last week!"
            context['dropHouse'] = f"Real Estate asset had a maximum drop of {bottom - top:.2f}!"

    if User.objects.filter(username='admin', id=uid).count() > 0:
        admin = User.objects.get(username='admin', id=uid)
        context['passcode'] = Hasher().hash(admin.checksum + datetime.now().strftime('%d/%m/%y')).encode('utf-8').hex()[:8]
    return render(request, 'index.html', context)

def index(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    context['stocks'] = Stock.objects.filter(asset__user__id=uid).all()
    context['cryptos'] = Crypto.objects.filter(asset__user__id=uid).all()
    context['vehicles'] = Vehicle.objects.filter(asset__user__id=uid).all()
    context['houses'] = House.objects.filter(asset__user__id=uid).all()

    now = datetime.now()
    weekAgo = now - timedelta(days=7)
    historyCrypto = (AssetHistory.objects
                     .filter(asset__category='C', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                     .order_by('record_date').all())
    historyStock = (AssetHistory.objects
                    .filter(asset__category='E', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                    .order_by('record_date').all())
    historyHouse = (AssetHistory.objects
                    .filter(asset__category='R', asset__user__id=uid, record_date__lte=now, record_date__gt=weekAgo)
                    .order_by('record_date').all())

    if len(historyCrypto) > 1:
        count = 0
        top = historyCrypto[0].record_value
        bottom = top
        for h in historyCrypto:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertCrypto'] = f"Crypto asset had frequent drops of {count} within the last week!"
            context['dropCrypto'] = f"Crypto asset had a maximum drop of {bottom - top:.2f}!"
    if len(historyStock) > 1:
        count = 0
        top = historyStock[0].record_value
        bottom = top
        for h in historyStock:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertStock'] = f"Stock asset had frequent drops of {count} within the last week!"
            context['dropStock'] = f"Stock asset had a maximum drop of {bottom - top:.2f}!"
    if len(historyHouse) > 1:
        count = 0
        top = historyHouse[0].record_value
        bottom = top
        for h in historyHouse:
            if h.record_value < top:
                count += 1
                if h.record_value < bottom:
                    bottom = h.record_value
        if count >= ALERT_COUNT:
            context['alertHouse'] = f"Real Estate asset had frequent drops of {count} within the last week!"
            context['dropHouse'] = f"Real Estate asset had a maximum drop of {bottom - top:.2f}!"

    if User.objects.filter(username='admin', id=uid).count() > 0:
        admin = User.objects.get(username='admin', id=uid)
        context['passcode'] = Hasher().hash(admin.checksum + datetime.now().strftime('%d/%m/%y')).encode('utf-8').hex()[:8]
    return render(request, 'index.html', context)


def vehicle(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            query = Vehicle.objects.filter(asset__user__id=uid)
            total = query.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = query.all()[(page-1)*size:page*size]
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
        user = User.objects.get(pk=uid)
        asset, _ = Asset.objects.get_or_create(category='V', user=user)
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
        targets = Vehicle.objects.filter(asset__user__id=uid).all()
        asset.purchase_price = sum([x.purchase_price for x in targets])
        asset.current_value = asset.purchase_price
        asset.save()
        Thread(target=update_current_values).start()
        return redirect('vehicle')

def house(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            query = House.objects.filter(asset__user__id=uid)
            total = query.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = query.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = page * size + len(data) != total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'house/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.edit:
            id = int(request.GET.get('id', 0))
            context['locations'] = LocationCategory.CHOICES
            context['proporty_types'] = PropertyType.CHOICES
            context['id'] = id
            if id > 0:
                context['data'] = House.objects.get(id=id)
            return render(request, 'house/edit.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                house_data = House.objects.get(id=id)
                context['data'] = house_data
                context['total_return'] = house_data.price_history[0]['value'] - house_data.purchase_price
                # Generate the Plot for html
                months = [p['month'].date() for p in house_data.price_history]
                prices = [p['value'] for p in house_data.price_history]
                matplotlib.use('Agg')
                fig, ax = plt.subplots()
                ax.plot(months, prices, label=house_data)
                ax.axhline(y=house_data.purchase_price, color='r', linestyle='--', label='Purchase Price')
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                ax.set_title(f'{house_data} House Price')
                plt.xticks(rotation=45)
                plt.tight_layout()
                ax.legend()
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                context['plot_url'] = f'data:image/png;base64,{plot_url}'
            return render(request, 'house/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        user = User.objects.get(pk=uid)
        asset, _ = Asset.objects.get_or_create(category='R', user=user)
        if _method == "delete":
            House.objects.get(id=id).delete()
        else:
            property_type = request.POST.get('property_type', "")
            address = request.POST.get('address', "")
            location = request.POST.get('location', "")
            street_number = request.POST.get('street_number', "")
            postal_code = request.POST.get('postal_code', "")
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
                address=address,
                street_number=street_number,
                postal_code=postal_code,
                location=location,
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
        targets = House.objects.filter(asset__user__id=uid).all()
        asset.purchase_price = sum([x.purchase_price for x in targets])
        asset.current_value = asset.purchase_price
        asset.save()
        Thread(target=update_current_values).start()
        return redirect('house')


def stock(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
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
            query = Stock.objects.filter(asset__user__id=uid)
            total = query.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = query.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = (page * size) < total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'stock/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.buy_or_sell:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Stock.objects.get(id=id)
            return render(request, 'stock/buy_or_sell.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.add:
            stock = Stock.objects.filter(ticker_symbol=ticker)
            if ticker:
                if stock:
                    context['data'] = stock[0]
                    return render(request, 'stock/buy_or_sell.html', context)
                return render(request, 'stock/add.html', context)
            else:
                return render(request, 'stock/new_stock.html')
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                stock_data = Stock.objects.get(id=id)
                context['data'] = stock_data

                transactions = StockTransaction.objects.filter(stock=stock_data).order_by('purchase_date')
                context['transactions'] = transactions

                initial_transaction = transactions[0]

                base_url = 'https://api.polygon.io/v2/aggs/ticker/'
                ticker = stock_data.ticker_symbol
                date_from = initial_transaction.purchase_date
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
                dates = [datetime.fromtimestamp(item['t'] / 1000).date() for item in data['results']]
                closing_prices = [item['c'] for item in data['results']]

                matplotlib.use('Agg')
                fig, ax = plt.subplots()
                ax.plot(dates, closing_prices, label=ticker)

                label_added = False
                start = 1
                for transaction in transactions:
                    if not label_added:
                        ax.plot(transaction.purchase_date, transaction.purchase_price, 'go', label='Transaction')
                        label_added = True
                        ax.annotate(
                            f'{start}',
                            (transaction.purchase_date, transaction.purchase_price),
                            textcoords='offset points',
                            xytext=(0, 5),
                            ha='center')
                        start += 1
                    else:
                        ax.plot(transaction.purchase_date, transaction.purchase_price, 'go')
                        ax.annotate(
                            f'{start}',
                            (transaction.purchase_date, transaction.purchase_price),
                            textcoords='offset points',
                            xytext=(0, 5),
                            ha='center')
                        start += 1

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
                total_cost = 0
                shares_owned = 0
                for transaction in transactions:
                    total_cost += transaction.share * transaction.purchase_price
                    shares_owned += transaction.share
                total_return = shares_owned * current_price - total_cost
                context['total_return'] = total_return

                return render(request, 'stock/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        user = User.objects.get(pk=uid)
        asset, _ = Asset.objects.get_or_create(category='E', user=user)
        if _method == "delete":
            Stock.objects.get(id=id).delete()
        elif _method == "buy_or_sell":
            buy_or_sell = request.POST.get('buy_or_sell', "")
            purchase_price = float(request.POST.get('purchase_price', ""))
            purchase_date = request.POST.get('purchase_date', "")
            stock = Stock.objects.get(id=id)
            if buy_or_sell == "sell":
                share = -int(request.POST.get('share', 0))
            else:
                share = int(request.POST.get('share', 0))
            transaction = StockTransaction(
                stock=stock,
                share=share,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            transaction.save()
            stock.update_on_transaction(transaction)
            stock.save()
        else:
            share = int(request.POST.get('share', 0))
            ticker_symbol = request.POST.get('ticker_symbol', "")
            market = request.POST.get('market', "")
            currency = request.POST.get('currency', "")
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            # user ticker_symbol+market unique check
            if Stock.objects.filter(asset__user=user, ticker_symbol=ticker_symbol, market=market).count() == 0:
                stock = Stock(
                    asset_id=asset.id,
                    share=share,
                    ticker_symbol=ticker_symbol,
                    market=market,
                    currency=currency,
                    purchase_price=purchase_price,
                    purchase_date=purchase_date)
                stock.save()
                initial_transaction = StockTransaction(
                    stock=stock,
                    share=share,
                    purchase_price=purchase_price,
                    purchase_date=purchase_date)
                initial_transaction.save()
        # update asset
        targets = Stock.objects.filter(asset__user__id=uid).all()
        asset.purchase_price = sum([x.purchase_price * x.share for x in targets])
        asset.current_value = asset.purchase_price
        asset.save()
        Thread(target=update_current_values).start()
        return redirect('stock')

def stock_search(request, stock_ticker):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if request.method == "GET":
        stock = Stock.objects.filter(ticker_symbol=stock_ticker)
        if stock:
            context["stock"] = stock[0]
            return render(request, '_stock_verify.html', context)
        else:
            context["stock"] = None
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


def crypto(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
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
        context['currency'] = results["currency_name"].upper()
    if request.method == "GET":
        viewtype = request.GET.get('vt', 'list')
        if VIEWTYPE[viewtype] is VIEWTYPE.list:
            query = Crypto.objects.filter(asset__user__id=uid)
            total = query.count()
            size = int(request.GET.get('size', 20))
            page = int(request.GET.get('page', 1))
            data = query.all()[(page-1)*size:page*size]
            context['total'] = total
            context['size'] = size
            context['page'] = page
            context['data'] = data
            context['hasPrev'] = page > 1
            context['hasNext'] = (page * size) < total
            context['pagePrev'] = page - 1
            context['pageNext'] = page + 1
            return render(request, 'crypto/index.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.buy_or_sell:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                context['data'] = Crypto.objects.get(id=id)
            return render(request, 'crypto/buy_or_sell.html', context)
        elif VIEWTYPE[viewtype] is VIEWTYPE.add:
            crypto = Crypto.objects.filter(ticker_symbol=ticker)
            if ticker:
                if crypto:
                    context['data'] = crypto[0]
                    return render(request, 'crypto/buy_or_sell.html', context)
                return render(request, 'crypto/add.html', context)
            else:
                return render(request, 'crypto/new_crypto.html')
        elif VIEWTYPE[viewtype] is VIEWTYPE.detail:
            id = int(request.GET.get('id', 0))
            context['id'] = id
            if id > 0:
                crypto_data = Crypto.objects.get(id=id)
                context['data'] = crypto_data

                transactions = CryptoTransaction.objects.filter(crypto=crypto_data).order_by('purchase_date')
                context['transactions'] = transactions

                initial_transaction = transactions[0]

                base_url = 'https://api.polygon.io/v2/aggs/ticker/'
                ticker = crypto_data.ticker_symbol
                date_from = initial_transaction.purchase_date
                date_to = datetime.now().date()
                purchase_price = crypto_data.purchase_price

                # Get the stock data
                url = f"{base_url}{ticker}/range/1/day/{date_from}/{date_to}"
                params = {
                    'apiKey': apikey,
                }
                response = requests.get(url, params=params)
                data = response.json()
                # Generate the Plot for html
                dates = [datetime.fromtimestamp(item['t'] / 1000).date() for item in data['results']]
                closing_prices = [item['c'] for item in data['results']]
                matplotlib.use('Agg')
                fig, ax = plt.subplots()
                ax.plot(dates, closing_prices, label=ticker)

                label_added = False
                start = 1
                for transaction in transactions:
                    if not label_added:
                        ax.plot(transaction.purchase_date, transaction.purchase_price, 'go', label='Transaction')
                        label_added = True
                        ax.annotate(
                            f'{start}',
                            (transaction.purchase_date, transaction.purchase_price),
                            textcoords='offset points',
                            xytext=(0, 5),
                            ha='center')
                        start += 1
                    else:
                        ax.plot(transaction.purchase_date, transaction.purchase_price, 'go')
                        ax.annotate(
                            f'{start}',
                            (transaction.purchase_date, transaction.purchase_price),
                            textcoords='offset points',
                            xytext=(0, 5),
                            ha='center')
                        start += 1
                
                ax.axhline(y=purchase_price, color='r', linestyle='--', label='Purchase Price')
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                ax.set_title(f'{ticker} Crypto Price')
                plt.xticks(rotation=45)
                plt.tight_layout()
                ax.legend()
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                context['plot_url'] = f'data:image/png;base64,{plot_url}'

                current_price = closing_prices[-1]
                total_cost = 0
                shares_owned = 0
                for transaction in transactions:
                    total_cost += transaction.share * transaction.purchase_price
                    shares_owned += transaction.share
                total_return = shares_owned * current_price - total_cost
                context['total_return'] = total_return

                return render(request, 'crypto/detail.html', context)
    if request.method == "POST":
        id = int(request.POST.get('id', 0))
        _method = request.POST.get('_method', None)
        user = User.objects.get(pk=uid)
        asset, _ = Asset.objects.get_or_create(category='C', user=user)
        if _method == "delete":
            Crypto.objects.get(id=id).delete()
        elif _method == "buy_or_sell":
            buy_or_sell = request.POST.get('buy_or_sell', "")
            purchase_price = float(request.POST.get('purchase_price', ""))
            purchase_date = request.POST.get('purchase_date', "")
            crypto = Crypto.objects.get(id=id)
            if buy_or_sell == "sell":
                share = -int(request.POST.get('share', 0))
            else:
                share = int(request.POST.get('share', 0))
            transaction = CryptoTransaction(
                crypto=crypto,
                share=share,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            transaction.save()
            crypto.update_on_transaction(transaction)
            crypto.save()
        else:
            share = int(request.POST.get('share', 0))
            ticker_symbol = request.POST.get('ticker_symbol', "")
            name = request.POST.get('name', "")
            currency = request.POST.get('currency', "")
            purchase_price = request.POST.get('purchase_price', "")
            purchase_date = request.POST.get('purchase_date', "")
            crypto = Crypto(
                asset_id=asset.id,
                share=share,
                ticker_symbol=ticker_symbol,
                name=name,
                currency=currency,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            crypto.save()
            initial_transaction = CryptoTransaction(
                crypto=crypto,
                share=share,
                purchase_price=purchase_price,
                purchase_date=purchase_date)
            initial_transaction.save()
        # update asset
        targets = Crypto.objects.filter(asset__user__id=uid).all()
        asset.purchase_price = sum([x.purchase_price * x.share for x in targets])
        asset.current_value = asset.purchase_price
        asset.save()
        Thread(target=update_current_values).start()
        return redirect('crypto')


def crypto_search(request, crypto_ticker):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if request.method == "GET":
        crypto = Crypto.objects.filter(ticker_symbol=crypto_ticker)
        if crypto:
            context["crypto"] = crypto[0]
            return render(request, '_crypto_verify.html', context)
        else:
            context["crypto"] = None
        crypto_ticker = crypto_ticker.upper()
        crypto_ticker = "X:" + crypto_ticker
        params = {
            "apiKey": "wW55pKJzExsThjPDizKdf8OAdDfkvLPW",
            "market": "crypto",
            "ticker": crypto_ticker,
            "limit": 10
        }
        response = requests.get("https://api.polygon.io/v3/reference/tickers", params=params)
        response_json = response.json()
        print(response_json)
        response_json_results = response_json["results"]
        result_count = len(response_json_results)
        result_list = []
        if result_count == 1:
            result_list.append(response_json_results[0])
        elif result_count == 0:
            params = {
                "apiKey": "wW55pKJzExsThjPDizKdf8OAdDfkvLPW",
                "market": "crypto",
                "search": crypto_ticker,
                "limit": 10
            }
            response = requests.get("https://api.polygon.io/v3/reference/tickers", params=params)
            response_json = response.json()
            print(response_json)
            response_json_results = response_json["results"]
            for result in response_json_results:
                result_list.append(result)
        context["result_count"] = result_count
        context["result_list"] = result_list
        return render(request, '_crypto_verify.html', context)

def user(request):
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if uid != str(ADMIN_ID):
        return redirect('home')
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
    uid = Cipher().decrypt(request.COOKIES.get(USER_ID, ''))
    if cache.get(uid, False) is not True:
        return redirect('login')
    context = {}
    context['isAdmin'] = uid == str(ADMIN_ID)
    if request.method == "GET":
        query = Asset.objects.filter(user__id=uid)
        total = query.count()
        size = int(request.GET.get('size', 20))
        page = int(request.GET.get('page', 1))
        data = query.all()[(page-1)*size:page*size]
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