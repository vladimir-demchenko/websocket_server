from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import requests
import time
from . import models, schemas, const, utils
from urllib.parse import urlparse
import random


def get_proxies(db: Session):
    return db.query(models.Proxy).all()


def get_proxy(proxy_id: int, db: Session):
    return db.query(models.Proxy).filter(models.Proxy.id == proxy_id).first()


def create_proxy(db: Session, proxy: schemas.ProxyCreate):
    db_proxy = models.Proxy(proxy_id=proxy.proxy_id, url=proxy.url,
                            change_ip=proxy.change_ip)
    db.add(db_proxy)
    db.commit()
    db.refresh(db_proxy)
    return db_proxy


def delete_proxy(db: Session, proxy_id: int):
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).delete()
    db.commit()
    return {'message': f'{proxy_id} deleted'}


def update_proxy(db: Session, id: int, proxy: schemas.ProxyCreate):
    db.query(models.Proxy).filter(models.Proxy.id == id).update(
        {models.Proxy.proxy_id: proxy.proxy_id, models.Proxy.url: proxy.url, models.Proxy.change_ip: proxy.change_ip})
    db.commit()
    return db.query(models.Proxy).filter(models.Proxy.id == id).first()


def get_configs(db: Session):
    return db.query(models.Config).all()


def get_config(db: Session, config_id: int):
    config = db.query(models.Config).filter(
        models.Config.id == config_id).first()

    if utils.sub_interval():
        interval = db.query(models.Interval).filter(
            models.Interval.time == utils.current_interval()).first()
        update_cities_click(interval=utils.sub_interval(),
                            target=interval.target, db=db)

    if (config.interval != utils.current_interval()):
        print("Change interval")
        reset_cities(db)
        reset_proxies(db)
        db.query(models.Config).update(
            {models.Config.interval: utils.current_interval()})
        proxies = db.query(models.Proxy).all()
        interval = db.query(models.Interval).filter(
            models.Interval.time == utils.current_interval()).first()
        for proxy in proxies:
            db.query(models.Proxy).filter(models.Proxy.id == proxy.id).update(
                {models.Proxy.targetClicks: (interval.target)/db.query(models.Proxy).count()})
        update_cities_click(interval=interval.time,
                            target=interval.target, db=db)
    db.commit()

    return db.query(models.Config).filter(
        models.Config.id == config_id).first()


def update_config(db: Session, config_id: int, config: schemas.ConfigClick):
    db.query(models.Config).filter(models.Config.id == config_id).update(
        {models.Config.url: config.url, models.Config.api_key: config.api_key, models.Config.pause: config.pause, models.Config.interval: config.interval})
    db.commit()
    return db.query(models.Config).filter(models.Config.id == config_id).first()


def create_config(db: Session, config: schemas.ConfigClickCreate):
    db_config = models.Config(api_key=config.api_key, url=config.url)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_intervals(db: Session):
    return db.query(models.Interval).all()


def create_interval(db: Session, interval: schemas.IntervalCreate):
    db_config = models.Interval(time=interval.time, target=interval.target)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_const():
    return const.const_cities


def update_const(id: str):
    const.const_cities[id]['counter'] += 1
    return const.const_cities


def click(db: Session, proxy_id: int):
    proxy = db.query(models.Proxy).filter(models.Proxy.id == proxy_id).first()
    parsed_url = urlparse(proxy.url).netloc
    credentials, host_port = parsed_url.split('@')
    login, password = credentials.split(':')
    host, port = host_port.split(':')

    # if get_proxy = null -> browser_create_proxy
    browser_proxies = requests.get('https://dolphin-anty-api.com/proxy', headers={
                                   'Authorization': f'Bearer {proxy.browser_api}'})
    browser_proxies_data = browser_proxies.json()['data']

    if not browser_proxies_data:
        create_proxy = requests.post('https://dolphin-anty-api.com/proxy?Content-Type=application/json', headers={
            'Authorization': f'Bearer {proxy.browser_api}'}, json={
            "type": "http",
            "host": f"{host}",
            "port": f"{port}",
            "login": f"{login}",
            "password": f"{password}",
            "name": "test"
        })
        print(create_proxy.text)

    # if when_change - now < 10min -> change_ip + create profile + click+1
    # else -> get_random_city + Proxy.city_id = res[0] + create_profile + click+1
    if time.time() - proxy.when_change < 600:
        city = db.query(models.City).filter(
            models.City.id == proxy.city_id).first()
        if city.counter == city.currentField:
            return {"status": "Fail", "message": "В данный момент нельзя поменять город", "time": proxy.when_change + 600}
        r_ip = requests.get(url=proxy.change_ip+'&format=json',
                            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})
        response = r_ip.json()
        print(r_ip.text)
        if 'error' in response or response['status'] == 'ERR':
            return {"status": "Fail", "message": "Ошибка! Попробуйте еще раз!"}
        print('Change ip')
    else:
        if proxy.city_id:
            db.query(models.City).filter(models.City.id ==
                                         proxy.city_id).update({models.City.taken: False})
        random_city = db.query(models.City).filter(
            models.City.taken == False, models.City.counter <= models.City.currentField).order_by(func.random()).first()
        db.query(models.City).filter(models.City.id ==
                                     random_city.id).update({models.City.taken: True})
        # if isinstance(result, str):
        #     print(result)
        #     return result
        config = db.query(models.Config).first()
        r_c = requests.get(url=f'https://mobileproxy.space/api.html?command=change_equipment&proxy_id={int(proxy.proxy_id)}&id_city={int(random_city.id)}',
                           headers={'Authorization': f"Bearer {config.api_key}"})
        response = r_c.json()
        print(response)
        if 'error' in response or response['status'] == 'err':
            return {"status": "Fail", "message": "Ошибка! Попробуйте еще раз!"}
        db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update({models.Proxy.city_id: random_city.id,
                                                                           models.Proxy.when_change: time.time()})
        db.commit()
        r_ip = requests.get(url=proxy.change_ip+'&format=json',
                            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})
        print('Change city')

    url = "https://dolphin-anty-api.com/browser_profiles"

    browser_proxies = requests.get('https://dolphin-anty-api.com/proxy', headers={
                                   'Authorization': f'Bearer {proxy.browser_api}'})
    browser_proxies_data = browser_proxies.json()['data']

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
            "id": browser_proxies_data[0]['id']
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {proxy.browser_api}'
    }

    response = requests.request("POST", url, headers=headers, json=data)

    upd_proxy = db.query(models.Proxy).filter(models.Proxy.id == proxy_id)
    upd_proxy.update({models.Proxy.clicks: models.Proxy.clicks + 1})
    db.query(models.City).filter(models.City.id == upd_proxy.first().city_id).update(
        {models.City.counter: models.City.counter + 1})
    db.commit()

    # print(r_ip.text)
    print(response.text)
    return response.json()


def test(db: Session):
    # clicks = db.query(models.Clicks).filter(
    #     models.Clicks.interval == '21:00').all()
    # for click in clicks:
    #     db.query(models.City).filter(models.City.id == click.city_id).update(
    #         {models.City.currentField: int(click.click_value * 2500)})
    #     db.commit()
    # return "Success"
    if utils.sub_interval():
        return "Success"
    else:
        return "None"
    # return create_cities(db)


def update_cities_click(interval: str, target: int, db: Session):
    clicks = db.query(models.Clicks).filter(
        models.Clicks.interval == interval).all()
    for click in clicks:
        db.query(models.City).filter(models.City.id == click.city_id).update(
            {models.City.currentField: int(click.click_value * target)})
        db.commit()


def get_clicks(db: Session):
    totalClicks = db.query(func.sum(models.City.currentField)).scalar()
    clicks = db.query(func.sum(models.City.counter)).scalar()
    return [clicks, totalClicks]


def reset_cities(db: Session):
    cities = db.query(models.City).all()
    for city in cities:
        db.query(models.City).filter(models.City.id == city.id).update(
            {models.City.currentField: int(0), models.City.taken: False, models.City.counter: 0})
        db.commit()
    return get_clicks(db)


def reset_proxies(db: Session):
    proxies = db.query(models.Proxy).all()
    for proxy in proxies:
        db.query(models.Proxy).filter(models.Proxy.id == proxy.id).update(
            {models.Proxy.targetClicks: 0, models.Proxy.clicks: 0})
        db.commit()


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


def create_cities(db: Session):
    for city_id, city_data in const.const_cities.items():
        db_city = models.City(id=city_id, name=city_data['name'])
        db.add(db_city)
        db.commit()
        db.refresh(db_city)
    for interval, clicks in const.click_config.items():
        for city_id, click_value in clicks.items():
            db_click = models.Clicks(
                city_id=city_id, interval=interval, click_value=click_value)
            db.add(db_click)
            db.commit()
            db.refresh(db_click)
    return "Success"
