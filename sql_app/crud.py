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
    parsed_url = urlparse(proxy.url).netloc
    credentials, host_port = parsed_url.split('@')
    login, password = credentials.split(':')
    host, port = host_port.split(':')

    browser_proxy = requests.post('https://dolphin-anty-api.com/proxy?Content-Type=application/json', headers={
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

    db_proxy = models.Proxy(proxy_id=response['data']['id'],
                            url=proxy.url, name=proxy.name, city_id=proxy.city_id)
    db.add(db_proxy)
    db.commit()
    db.refresh(db_proxy)

    return db_proxy


def delete_proxy(db: Session, proxy_id: int):
    request_proxy = db.query(models.Proxy).filter(models.Proxy.id == proxy_id)
    headers = {
        'Authorization': f'Bearer {getenv("API_KEY")}'
    }
    delete_request = requests.delete(f'https://dolphin-anty-api.com/proxy/{request_proxy.first().proxy_id}', headers=headers)

    if delete_request.status_code == 200:
        request_proxy.delete()
        db.commit()
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

def take_proxy(proxy_id: int, db: Session):
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update({models.Proxy.taken: True})
    db.commit()
    return db.query(models.Proxy).filter(models.Proxy.id == proxy_id).first()

def untake_proxy(proxy_id: int, db: Session):
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update({models.Proxy.taken: False})
    db.commit()
    return db.query(models.Proxy).filter(models.Proxy.id == proxy_id).first()

def get_configs(db: Session):
    return db.query(models.Config).all()


def get_config(db: Session, config_id: int):
    config = db.query(models.Config).filter(
        models.Config.id == config_id).first()

    
    return config


def update_config(db: Session, config_id: int, config: schemas.ConfigClick):
    db.query(models.Config).filter(models.Config.id == config_id).update(
        {models.Config.url: config.url, models.Config.api_key: config.api_key, models.Config.delay: config.delay, models.Config.interval: config.interval})
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


def create_profile(proxy_id: int):
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
        'Authorization': f'Bearer {getenv("API_KEY")}'
    }

    response = requests.request("POST", url, headers=headers, json=data)

    # print(r_ip.text)
    print(response.text)
    return response.json()


def delete_profile(profile_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {getenv("API_KEY")}'
    }

    response = requests.delete(f'https://dolphin-anty-api.com/browser_profiles/{profile_id}?forceDelete=1', headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(400, response.json())


def test(db: Session):
    return db.query(models.Proxy).join(models.City).filter(models.Proxy.id == 1).first()


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


def reset_cities(interval: schemas.ResetCity, db: Session):
    target = db.query(models.Interval).filter(models.Interval.time == interval.interval).first()
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
    db_city = models.City(name=city.name, short_name=city.short_name)
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
    db.commit()
    return {'success': True}