from sqlalchemy.orm import Session
import requests
import time
from . import models, schemas, const, utils
from urllib.parse import urlparse


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
    return db.query(models.Config).filter(models.Config.id == config_id).first()


def update_config(db: Session, config_id: int, config: schemas.ConfigClick):
    db.query(models.Config).filter(models.Config.id == config_id).update(
        {models.Config.url: config.url, models.Config.api_key: config.api_key, models.Config.pause: config.pause})
    db.commit()
    return db.query(models.Config).filter(models.Config.id == config_id).first()


def create_config(db: Session, config: schemas.ConfigClickCreate):
    db_config = models.Config(api_key=config.api_key, url=config.url)
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
    # if time.time() - proxy.when_change < 600:
    r_ip = requests.get(url=proxy.change_ip+'&format=json',
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})
    print(r_ip.text)
    # else:
    #     if proxy.city_id:
    #         const.const_cities[proxy.city_id]['taken'] = False
    #     result = utils.get_random_city(const.const_cities)
    #     if isinstance(result, str):
    #         print(result)
    #         return result
    #     db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update({models.Proxy.city_id: result[0],
    #                                                                        models.Proxy.when_change: time.time()})
    #     db.commit()
    #     # r_ip = requests.get(url=proxy.change_ip+'&format=json',
    #                     headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})

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

    # print(r_ip.text)
    print(response.text)
    return response.json()


def test():
    # utils.update_start_field(
    #     const.const_cities, const.click_config['09:00-17:00'], const.interval_config['09:00-17:00'])
    # return utils.get_random_city(const.const_cities)
    return utils.current_interval()


def update_browser_config(db: Session, proxy_id: int, browser_api: schemas.BrowserApi):
    print(browser_api)
    db.query(models.Proxy).filter(models.Proxy.id == proxy_id).update(
        {models.Proxy.browser_api: browser_api.browser_api})
    db.commit()
    return "success"
