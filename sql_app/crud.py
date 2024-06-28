from sqlalchemy.orm import Session
import requests

from . import models, schemas

const_cities = {
    '1': {
        'name': 'Москва',
        'StartField': 0,
        'CurrentField': 0,
        'taken': False,
        'counter': 0
    },
    '1060': {
        'name': 'Сочи',
        'StartField': 15,
        'CurrentField': 0,
        'taken': False,
        'counter': 0
    },
    "17590": {
        "name": "Семаранг",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "17591": {
        "name": "Пхукет",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "17592": {
        "name": "Пекалонган",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "17593": {
        "name": "Денпасар",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "15552": {
        "name": "Бангкок",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "8809": {
        "name": "Дели",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "8828": {
        "name": "Лудхияна",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "8844": {
        "name": "Джакарта",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "3511": {
        "name": "Перт",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1921": {
        "name": "Екатеринбург",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "2090": {
        "name": "Казань",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "2175": {
        "name": "Томск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "2272": {
        "name": "Сургут",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1596": {
        "name": "Владивосток",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1342": {
        "name": "Нижний Новгород",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1406": {
        "name": "Новосибирск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1287": {
        "name": "Мурманск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1042": {
        "name": "Краснодар",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "1116": {
        "name": "Красноярск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "733": {
        "name": "Иркутск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "315": {
        "name": "Архангельск",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "173": {
        "name": "Санкт-Петербург",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "14031": {
        "name": "Майами",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "14149": {
        "name": "Чикаго",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False

    },
    "14670": {
        "name": "Нью-Йорк",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "15084": {
        "name": "Филадельфия",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "15186": {
        "name": "Хьюстон",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "12144": {
        "name": "Амстердам",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "12204": {
        "name": "Утрехт",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "12233": {
        "name": "Делфт",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "12814": {
        "name": "Краков",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "12816": {
        "name": "Варшава",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "13112": {
        "name": "Лиссабон",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "15939": {
        "name": "Хельсинки",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "16130": {
        "name": "Ницца",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "16492": {
        "name": "Париж",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
    "16675": {
        "name": "Прага",
        'StartField': 300,
        'CurrentField': 0,
        'counter': 0,
        'taken': False
    },
}


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
    return const_cities


def update_const(id: str):
    const_cities[id]['counter'] += 1
    return const_cities


def click(db: Session, proxy_id: int):
    proxy = db.query(models.Proxy).filter(models.Proxy.id == proxy_id).first()
    r_ip = requests.get(url=proxy.change_ip+'&format=json',
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})

    print(r_ip.text)
    return r_ip.json()
