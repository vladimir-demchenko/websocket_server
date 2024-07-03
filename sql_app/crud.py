from sqlalchemy.orm import Session
import requests
import time
from . import models, schemas, const, utils
import re


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
    # r_ip = requests.get(url=proxy.change_ip+'&format=json',
    #                     headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})

    url = "https://dolphin-anty-api.com/browser_profiles"

    payload = f'name=Proxy_{time.time()}&tags%5B%5D=&tabs=&platform=windows&platformVersion=15.0.0&mainWebsite=none&useragent%5Bmode%5D=manual&useragent%5Bvalue%5D=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36&webrtc%5Bmode%5D=altered&webrtc%5BipAddress%5D=&canvas%5Bmode%5D=real&webgl%5Bmode%5D=real&webglInfo%5Bmode%5D=manual&webglInfo%5Bvendor%5D=Google Inc. (AMD)&webglInfo%5Brenderer%5D=ANGLE (AMD, Radeon (TM) RX 470 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)&webglInfo%5Bwebgl2Maximum%5D=%7B%5C%22MAX_SAMPLES%5C%22%3A%208%2C%20%5C%22MAX_DRAW_BUFFERS%5C%22%3A%208%2C%20%5C%22MAX_TEXTURE_SIZE%5C%22%3A%2016384%2C%20%5C%22MAX_ELEMENT_INDEX%5C%22%3A%204294967294%2C%20%5C%22MAX_VIEWPORT_DIMS%5C%22%3A%20%5B16384%2C%2016384%5D%2C%20%5C%22MAX_VERTEX_ATTRIBS%5C%22%3A%2016%2C%20%5C%22MAX_3D_TEXTURE_SIZE%5C%22%3A%202048%2C%20%5C%22MAX_VARYING_VECTORS%5C%22%3A%2030%2C%20%5C%22MAX_ELEMENTS_INDICES%5C%22%3A%202147483647%2C%20%5C%22MAX_TEXTURE_LOD_BIAS%5C%22%3A%2015%2C%20%5C%22MAX_COLOR_ATTACHMENTS%5C%22%3A%208%2C%20%5C%22MAX_ELEMENTS_VERTICES%5C%22%3A%202147483647%2C%20%5C%22MAX_RENDERBUFFER_SIZE%5C%22%3A%2016384%2C%20%5C%22MAX_UNIFORM_BLOCK_SIZE%5C%22%3A%2065536%2C%20%5C%22MAX_VARYING_COMPONENTS%5C%22%3A%20120%2C%20%5C%22MAX_TEXTURE_IMAGE_UNITS%5C%22%3A%2032%2C%20%5C%22MAX_ARRAY_TEXTURE_LAYERS%5C%22%3A%202048%2C%20%5C%22MAX_PROGRAM_TEXEL_OFFSET%5C%22%3A%207%2C%20%5C%22MIN_PROGRAM_TEXEL_OFFSET%5C%22%3A%20-8%2C%20%5C%22MAX_CUBE_MAP_TEXTURE_SIZE%5C%22%3A%2016384%2C%20%5C%22MAX_VERTEX_UNIFORM_BLOCKS%5C%22%3A%2013%2C%20%5C%22MAX_VERTEX_UNIFORM_VECTORS%5C%22%3A%204096%2C%20%5C%22MAX_COMBINED_UNIFORM_BLOCKS%5C%22%3A%2060%2C%20%5C%22MAX_FRAGMENT_UNIFORM_BLOCKS%5C%22%3A%2013%2C%20%5C%22MAX_UNIFORM_BUFFER_BINDINGS%5C%22%3A%2072%2C%20%5C%22MAX_FRAGMENT_UNIFORM_VECTORS%5C%22%3A%204096%2C%20%5C%22MAX_VERTEX_OUTPUT_COMPONENTS%5C%22%3A%20124%2C%20%5C%22MAX_FRAGMENT_INPUT_COMPONENTS%5C%22%3A%20124%2C%20%5C%22MAX_VERTEX_UNIFORM_COMPONENTS%5C%22%3A%2016384%2C%20%5C%22MAX_VERTEX_TEXTURE_IMAGE_UNITS%5C%22%3A%2032%2C%20%5C%22MAX_FRAGMENT_UNIFORM_COMPONENTS%5C%22%3A%2016384%2C%20%5C%22UNIFORM_BUFFER_OFFSET_ALIGNMENT%5C%22%3A%20256%2C%20%5C%22MAX_COMBINED_TEXTURE_IMAGE_UNITS%5C%22%3A%2064%2C%20%5C%22MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS%5C%22%3A%20229376%2C%20%5C%22MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS%5C%22%3A%204%2C%20%5C%22MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS%5C%22%3A%20229376%2C%20%5C%22MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS%5C%22%3A%204%2C%20%5C%22MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS%5C%22%3A%20128%7D%22%0Awebrtc%3A%20%7Bmode%3A%20%22altered%22%2C%20ipAddress%3A%20null%7D&notes%5Bicon%5D=&notes%5Bcolor%5D=&notes%5Bstyle%5D=&notes%5Bcontent%5D=&timezone%5Bmode%5D=auto&timezone%5Bvalue%5D=&locale%5Bmode%5D=&locale%5Bvalue%5D=&statusId=&geolocation%5Bmode%5D=&geolocation%5Blatitude%5D=&geolocation%5Blongitude%5D=&cpu%5Bmode%5D=manual&cpu%5Bvalue%5D=4&memory%5Bmode%5D=manual&memory%5Bvalue%5D=8&doNotTrack=0&browserType=anty&proxy%5Bid%5D=&proxy%5Btype%5D=&proxy%5Bhost%5D=&proxy%5Bport%5D=&proxy%5Blogin%5D=&proxy%5Bpassword%5D=&proxy%5Bname%5D=&proxy%5BchangeIpUrl%5D='
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
            "id": 360498298
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
