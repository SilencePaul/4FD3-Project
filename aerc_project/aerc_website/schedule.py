from apscheduler.schedulers.background import BackgroundScheduler
from .models import Vehicle, House, Crypto, Stock, User, Asset, AssetType, LocationCategory
from datetime import datetime, timedelta
import requests

def get_vehicles_value(vehicles, default):
    return default*0.9

def get_houses_value(houses, default):
    res = 0
    for h in houses:
        res += h.price_history[-1]['value']
    return res
    # return default*0.96

def get_cryptos_value(cryptos, default):
    return default*0.95

def get_stocks_value(stocks, default):
    res = 0
    apikey = "wW55pKJzExsThjPDizKdf8OAdDfkvLPW"
    base_url = 'https://api.polygon.io/v2/aggs/ticker/'
    for s in stocks:
        ticker = s.ticker_symbol
        date_from = (datetime.now() - timedelta(days=1)).date()
        date_to = datetime.now().date()

        # Get the stock data
        url = f"{base_url}{ticker}/range/1/day/{date_from}/{date_to}"
        params = {
            'apiKey': apikey,
        }
        response = requests.get(url, params=params)
        data = response.json()
        if "results" in data:
            results = data["results"]
            last = len(results)-1
            res += results[last]['c']
    return res
    #return default*0.95

def update_current_values():
    asset_vehicle = Asset.objects.get(category='V')
    asset_vehicle.current_value = get_vehicles_value(
        Vehicle.objects.all(),
        asset_vehicle.purchase_price
    )
    asset_vehicle.save()

    asset_house = Asset.objects.get(category='R')
    asset_house.current_value = get_houses_value(
        House.objects.all(),
        asset_house.purchase_price
    )
    asset_house.save()

    asset_crypto = Asset.objects.get(category='C')
    asset_crypto.current_value = get_cryptos_value(
        Crypto.objects.all(),
        asset_crypto.purchase_price
    )
    asset_crypto.save()

    asset_stock = Asset.objects.get(category='E')
    asset_stock.current_value = get_stocks_value(
        Stock.objects.all(),
        asset_stock.purchase_price
    )
    asset_stock.save()

def setup_schedule():
    update_current_values()
    scheduler = BackgroundScheduler()
    try:
        scheduler.add_job(update_current_values, 'interval', hours=1,
                          id='update_current_values', replace_existing=True)
        scheduler.start()
    except Exception as e:
        print(e)
        scheduler.shutdown()