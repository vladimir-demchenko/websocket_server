from sqlalchemy.orm import Session

from . import models, schemas


def get_proxies(db: Session):
    return db.query(models.Proxy).all()


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
