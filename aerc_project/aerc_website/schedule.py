from apscheduler.schedulers.background import BackgroundScheduler
from .models import Vehicle, House, Crypto, Stock, User, Asset, AssetType, LocationCategory, AssetHistory
from datetime import datetime, timedelta
import requests
import json

def get_vehicles_value(vehicles, default):
    try:
        1/0
    except:
        return default*0.9966

def get_houses_value(houses, default):
    try:
        res = 0
        for h in houses:
            res += h.price_history[-1]['value']
        return res
    except:
        return default*0.9966

def get_cryptos_value(cryptos, default):
    try:
        res = 0
        apikey = "wW55pKJzExsThjPDizKdf8OAdDfkvLPW"
        base_url = 'https://api.polygon.io/v2/aggs/ticker/'
        for c in cryptos:
            ticker = c.ticker_symbol
            share = c.share
            date_from = (datetime.now() - timedelta(days=1)).date()
            date_to = datetime.now().date()

            # Get the stock data
            url = f"{base_url}{ticker}/range/1/day/{date_from}/{date_to}"
            params = {
                'apiKey': apikey,
            }
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data))
            if "results" in data:
                results = data["results"]
                last = len(results)-1
                res += results[last]['c'] * share
            else:
                raise
        return res
    except:
        return default*0.9955

def get_stocks_value(stocks, default):
    try:
        res = 0
        apikey = "wW55pKJzExsThjPDizKdf8OAdDfkvLPW"
        base_url = 'https://api.polygon.io/v2/aggs/ticker/'
        for s in stocks:
            ticker = s.ticker_symbol
            share = s.share
            date_from = (datetime.now() - timedelta(days=1)).date()
            date_to = datetime.now().date()

            # Get the stock data
            url = f"{base_url}{ticker}/range/1/day/{date_from}/{date_to}"
            params = {
                'apiKey': apikey,
            }
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data))
            if "results" in data:
                results = data["results"]
                last = len(results)-1
                res += results[last]['c'] * share
            else:
                raise
        return res
    except:
        return default*0.9955

def update_current_values():
    today = datetime.today()
    users = User.objects.all()
    for u in users:
        if Asset.objects.filter(category='V', user__id=u.id).count() > 0:
            asset_vehicle = Asset.objects.get(category='V', user__id=u.id)
            if asset_vehicle.purchase_price == 0:
                asset_vehicle.current_value = 0
            else:
                asset_vehicle.current_value = get_vehicles_value(
                    Vehicle.objects.filter(asset=asset_vehicle).all(),
                    asset_vehicle.current_value
                )
            asset_vehicle.save()
            if AssetHistory.objects.filter(asset=asset_vehicle, record_date=today).count() > 0:
                historyVehicle = AssetHistory.objects.get(asset=asset_vehicle, record_date=today)
                historyVehicle.record_value = asset_vehicle.current_value
                historyVehicle.save()
            else:
                AssetHistory(asset=asset_vehicle, record_date=today, record_value=asset_vehicle.current_value).save()

        if Asset.objects.filter(category='R', user__id=u.id).count() > 0:
            asset_house = Asset.objects.get(category='R', user__id=u.id)
            if asset_house.purchase_price == 0:
                asset_house.current_value = 0
            else:
                asset_house.current_value = get_houses_value(
                    House.objects.filter(asset=asset_house).all(),
                    asset_house.current_value
                )
            asset_house.save()
            if AssetHistory.objects.filter(asset=asset_house, record_date=today).count() > 0:
                historyHouse = AssetHistory.objects.get(asset=asset_house, record_date=today)
                historyHouse.record_value = asset_house.current_value
                historyHouse.save()
            else:
                AssetHistory(asset=asset_house, record_date=today, record_value=asset_house.current_value).save()

        if Asset.objects.filter(category='C', user__id=u.id).count() > 0:
            asset_crypto = Asset.objects.get(category='C', user__id=u.id)
            if asset_crypto.purchase_price == 0:
                asset_crypto.current_value = 0
            else:
                asset_crypto.current_value = get_cryptos_value(
                    Crypto.objects.filter(asset=asset_crypto).all(),
                    asset_crypto.current_value
                )
            asset_crypto.save()
            if AssetHistory.objects.filter(asset=asset_crypto, record_date=today).count() > 0:
                historyCrypto = AssetHistory.objects.get(asset=asset_crypto, record_date=today)
                historyCrypto.record_value = asset_crypto.current_value
                historyCrypto.save()
            else:
                AssetHistory(asset=asset_crypto, record_date=today, record_value=asset_crypto.current_value).save()

        if Asset.objects.filter(category='E', user__id=u.id).count() > 0:
            asset_stock = Asset.objects.get(category='E', user__id=u.id)
            if asset_stock.purchase_price == 0:
                asset_stock.current_value = 0
            else:
                asset_stock.current_value = get_stocks_value(
                    Stock.objects.filter(asset=asset_stock).all(),
                    asset_stock.current_value
                )
            asset_stock.save()
            if AssetHistory.objects.filter(asset=asset_stock, record_date=today).count() > 0:
                historyStock = AssetHistory.objects.get(asset=asset_stock, record_date=today)
                historyStock.record_value = asset_stock.current_value
                historyStock.save()
            else:
                AssetHistory(asset=asset_stock, record_date=today, record_value=asset_stock.current_value).save()

def setup_schedule():
    scheduler = BackgroundScheduler()
    try:
        update_current_values()
        scheduler.add_job(update_current_values, 'interval', hours=1,
                          id='update_current_values', replace_existing=True)
        scheduler.start()
    except Exception as e1:
        print(e1)
        try:
            scheduler.shutdown()
        except Exception as e2:
            print(e2)
