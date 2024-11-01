from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
import requests
import time
from . import models, schemas, const, utils
from urllib.parse import urlparse
import math
from os import getenv
from fastapi import HTTPException
from datetime import datetime


def get_proxies(db: Session):
    return db.query(models.Proxy).join(models.City).options(joinedload(models.Proxy.city)).all()


def get_proxy(proxy_id: int, db: Session):
    return db.query(models.Proxy).join(models.City).filter(models.Proxy.id == proxy_id).options(joinedload(models.Proxy.city)).first()


def create_proxy(db: Session, proxy: schemas.ProxyCreate):
    db_proxy = models.Proxy(url=proxy.url, name=proxy.name, city_id=proxy.city_id, proxy_id=0)
    db.add(db_proxy)
    db.commit()
    db.refresh(db_proxy)

    return db_proxy

def create_browser_proxy(browser_api: str, proxy: schemas.Proxy):
    parsed_url = urlparse(proxy.url).netloc
    credentials, host_port = parsed_url.split('@')
    login, password = credentials.split(':')
    host, port = host_port.split(':')

    browser_proxy = requests.post('https://dolphin-anty-api.com/proxy?Content-Type=application/json', headers={
        'Authorization': f'Bearer {browser_api}'}, json={
        "type": "http",
        "host": f"{host}",
        "port": f"{port}",
        "login": f"{login}",
        "password": f"{password}",
        "name": f"{proxy.name}"
    })

    response = browser_proxy.json()
    return response

def delete_proxy(db: Session, proxy_id: int):
    request_proxy = db.query(models.Proxy).filter(models.Proxy.id == proxy_id)

    request_proxy.delete()
    db.commit()
    return {'message': f'{proxy_id} deleted'}

    
def delete_browser_proxy(browser_api: str, proxy_id: int):
    headers = {
        'Authorization': f'Bearer {browser_api}'
    }
    delete_request = requests.delete(f'https://dolphin-anty-api.com/proxy/{proxy_id}', headers=headers)

    if delete_request.status_code == 200:
        return {'message': f'{proxy_id} deleted'}
    else: 
        raise HTTPException(400, delete_request.json())

def update_proxy(db: Session, id: int, proxy: schemas.ProxyUpdate):
    parsed_url = urlparse(proxy.url).netloc
    credentials, host_port = parsed_url.split('@')
    login, password = credentials.split(':')
    host, port = host_port.split(':')

    browser_proxy = requests.patch(f'https://dolphin-anty-api.com/proxy/{proxy.proxy_id}?Content-Type=application/json', headers={
        'Authorization': f'Bearer {getenv("API_KEY")}'}, json={
        "type": "http",
        "host": f"{host}",
        "port": f"{port}",
        "login": f"{login}",
        "password": f"{password}",
        "name": f"{proxy.name}"
    })

    response = browser_proxy.json()
    print(response)
    db.query(models.Proxy).filter(models.Proxy.id == id).update(
        {models.Proxy.url: proxy.url, models.Proxy.city_id: proxy.city_id, models.Proxy.name: proxy.name, models.Proxy.proxy_id: proxy.proxy_id})
    db.commit()
    return db.query(models.Proxy).filter(models.Proxy.id == id).first()


def get_random_proxy(db: Session):
    print()
    return db.query(models.Proxy)\
        .join(models.City)\
        .filter(models.Proxy.taken == False)\
        .filter(models.City.counter <= models.City.currentField)\
        .group_by(func.random())\
        .options(joinedload(models.Proxy.city)).first()

def take_proxy(client_id: int, db: Session):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    random_proxy = get_random_proxy(db=db)
    if not random_proxy:
        return {"status": False, "result": {}}
    random_proxy.taken = True
    db.commit()
    db.refresh(random_proxy)

    browser_proxy = create_browser_proxy(client.browser_api, random_proxy)

    create_response = create_profile(browser_api=client.browser_api, proxy_id=browser_proxy['data']['id'])
    
    return {"status": True, "result": {"profile": create_response, "proxy": random_proxy, "browser_proxy": browser_proxy}}

def untake_proxy(client_id: int, profile_id: int, browser_proxy_id: int, proxy_id: int, db: Session):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update({models.Proxy.taken: False})
    db.commit()
    delete_profile_response = delete_profile(client.browser_api,profile_id)
    delete_proxy_response = delete_browser_proxy(client.browser_api, browser_proxy_id)

    return {"status": True, "result": {"profile": delete_profile_response, "browser_proxy": delete_proxy_response}}

def get_configs(db: Session):
    return db.query(models.Config).all()


def get_config(db: Session, config_id: int):
    config = db.query(models.Config).filter(
        models.Config.id == config_id).first()

    
    return config


def update_config(db: Session, config_id: int, config: schemas.ConfigClick):
    db.query(models.Config).filter(models.Config.id == config_id).update(
        {models.Config.url: config.url, models.Config.api_key: config.api_key, models.Config.delay: config.delay, models.Config.interval: config.interval, models.Config.threads: config.threads})
    db.commit()
    return db.query(models.Config).filter(models.Config.id == config_id).first()


def create_config(db: Session, config: schemas.ConfigClickCreate):
    db_config = models.Config(api_key=config.api_key, url=config.url, delay=config.delay, interval=config.interval)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_config(config_id: int, db: Session):
    db.query(models.Config).filter(models.Config.id == config_id).delete()
    db.commit()
    return {"success": True}

def get_intervals(db: Session):
    return db.query(models.Interval).all()


def create_interval(db: Session, interval: schemas.IntervalCreate):
    db_config = models.Interval(time=interval.time, target=interval.target)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_interval(interval_id: int, interval: schemas.IntervalCreate, db: Session):
    db.query(models.Interval).filter(models.Interval.id == interval_id).update({models.Interval.time: interval.time, models.Interval.target: interval.target})
    db.commit()

    return db.query(models.Interval).filter(models.Interval.id == interval_id).first()


def create_profile(browser_api:str, proxy_id: int):
    url = "https://dolphin-anty-api.com/browser_profiles"

    data = {
        "name": f'Proxy_{time.time()}',
        "platform": "windows",
        "platformVersion": "15.0.0",
        "mainWebsite": "none",
        "useragent": {
            "mode": "manual",
            "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        },
        "webrtc": {
            "mode": "altered",
            "ipAddress": None
        },
        "canvas": {
            "mode": "real"
        },
        "webgl": {
            "mode": "real"
        },
        "webglInfo": {
            "mode": "random"
        },
        "timezone": {
            "mode": "auto"
        },
        "locale": {
            "mode": "auto"
        },
        "cpu": {
            "mode": "manual",
            "value": 4
        },
        "memory": {
            "mode": "manual",
            "value": 8
        },
        "doNotTrack": "0",
        "browserType": "anty",
        "proxy": {
            "id": proxy_id
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {browser_api}'
    }

    response = requests.request("POST", url, headers=headers, json=data)

    # print(r_ip.text)
    print(response.text)
    return response.json()


def delete_profile(browser_api: str, profile_id:int):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {browser_api}'
    }

    response = requests.delete(f'https://dolphin-anty-api.com/browser_profiles/{profile_id}?forceDelete=1', headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(400, response.json())


def test(db: Session):
    return db.query(models.Clicks).all()


def update_cities_click(interval: str, target: int, db: Session):
    clicks = db.query(models.Clicks).filter(
        models.Clicks.interval == interval).all()
    for click in clicks:
        db.query(models.City).filter(models.City.id == click.city_id).update(
            {models.City.currentField: math.ceil(click.click_value * target)})
        db.commit()


def get_clicks(db: Session):
    totalClicks = db.query(func.sum(models.City.currentField)).scalar()
    clicks = db.query(func.sum(models.City.counter)).scalar()
    return [clicks, totalClicks]

def time_to_seconds(time_str):
    """Convert time (HH:MM) to seconds since midnight."""
    time_obj = datetime.strptime(time_str, "%H:%M")
    return time_obj.hour * 3600 + time_obj.minute * 60

def calculate_interval_seconds(time_range):
    """
    Calculate the total seconds between the start and end times
    provided as a time range (e.g., "09:00-17:00"), handling midnight wraparound.
    """
    start_time, end_time = time_range.split('-')
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    
    if end_seconds < start_seconds:
        # Handle crossing midnight by adding 24 hours (86400 seconds)
        return (86400 - start_seconds) + end_seconds
    else:
        return end_seconds - start_seconds


def reset_cities(interval: str, db: Session):
    target = db.query(models.Interval).filter(models.Interval.time == interval).first()
    cities = db.query(models.City).all()

    update_data = []

    for city in cities:
        new_current_field = math.ceil(city.city_value * target.target)

        # Append the update mapping for each city
        update_data.append({
            'id': city.id,  # Required for identifying which row to update
            'currentField': new_current_field,  # New calculated value
            'taken': False,  # Reset taken flag
            'counter': 0     # Reset counter
        })

    if interval == '09:00-17:00':
        clicks = models.Clicks(date=datetime.now())
        db.add(clicks)
    
    config = get_config(db, 1)
    new_delay = (calculate_interval_seconds(target.time) / target.target) // config.threads

    db.bulk_update_mappings(models.City, update_data)
    db.query(models.Config).filter(models.Config.id == 1).update({models.Config.interval: target.time, models.Config.delay: new_delay })

    db.commit()
    
    return db.query(models.City).all()


def reset_proxies(db: Session):
    proxies = db.query(models.Proxy).all()
    update_data = []

    for proxy in proxies:
        # Append the update mapping for each city
        update_data.append({
            'id': proxy.id,  # Required for identifying which row to update
            'taken': False,  # Reset taken flag
        })

    db.bulk_update_mappings(models.Proxy, update_data)
    db.commit()

    return db.query(models.Proxy).all()


def get_cities(db: Session):
    return db.query(models.City).all()


def get_city(city_id: str, db: Session):
    return db.query(models.City).filter(models.City.id == city_id).first()


def update_browser_config(db: Session, proxy_id: int, browser_api: schemas.BrowserApi):
    print(browser_api)
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update(
        {models.Proxy.browser_api: browser_api.browser_api})
    db.commit()
    return "success"


def create_cities(db: Session, city: schemas.CityCreate):
    db_city = models.City(name=city.name, short_name=city.short_name, city_value=city.city_value)
    db.add(db_city)
    db.commit()
    db.refresh(db_city)

    return db_city

def update_cities(city_id: int, city: schemas.CityUpdate, db: Session):
    db.query(models.City).filter(models.City.id == city_id).update({models.City.city_value: city.city_value, models.City.name: city.name, models.City.short_name: city.short_name})
    db.commit()
    return db.query(models.City).filter(models.City.id == city_id).first()

def delete_city(city_id: int, db: Session):
    db.query(models.City).filter(models.City.id == city_id).delete()
    db.commit()
    return {"success": True}

def click(city_id: int, db: Session):
    db.query(models.City).filter(models.City.id == city_id).update({models.City.counter: models.City.counter + 1})
    latest_date = db.query(models.Clicks).order_by(models.Clicks.date.desc()).first()
    latest_date.clicks += 1
    db.commit()
    db.refresh(latest_date)
    return {'success': True}

def create_client(client: schemas.ClientCreate, db: Session):
    db_client = models.Client(name=client.name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client

def get_clients(db: Session):
    return db.query(models.Client).all()

def get_client(client_id: int, db: Session):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def update_client( client_id: int,client: schemas.ClientUpdate, db: Session):
    db.query(models.Client).filter(models.Client.id == client_id).update({models.Client.name: client.name, models.Client.browser_api: client.browser_api})
    db.commit()

    return {'success': True}

def delete_client(client_id: int, db: Session):
    db.query(models.Client).filter(models.Client.id == client_id).delete()
    db.commit()
    return {"success": True}

def find_current_interval(intervals, current_time):
    for interval in intervals:
        
        # Split the time into start and end times
        start_time_str, end_time_str = interval.time.split("-")
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        # Check if the current time falls within the interval
        if start_time <= current_time <= end_time:
            return interval
        # Handle intervals that go past midnight (e.g., 21:00-00:00)
        elif start_time > end_time and (start_time <= current_time or current_time <= end_time):
            return interval
    
    return None  # Return None if no interval matches

def schedule_reset(now: schemas.ScheduleCheck, db: Session):
    intervals = get_intervals(db)
    config = get_config(db,1)
    current_time = datetime.fromisoformat(now.now)

        # If no scheduled time fetched, keep trying
    if not intervals:
        return {"status": False, "message": "No valid scheduled time found. Retrying in 60 seconds..."}
       

    # Check if it's the scheduled time
    if find_current_interval(intervals=intervals, current_time=current_time.time()).time != config.interval:
        return reset_cities(find_current_interval(intervals=intervals, current_time=current_time.time()).time, db)
        # Wait to avoid running the task multiple times in the same minute

  