from sqlalchemy import Boolean, Column, ForeignKey, String, Integer

from .database import Base


class Proxy(Base):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proxy_id = Column(String)
    url = Column(String)
    when_change = Column(Integer, default=0)
    change_ip = Column(String)
    taken = Column(Boolean, default=False)
    browser_api = Column(String, default='')
    city_id = Column(String, default='')


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pause = Column(Boolean, default=True)
    api_key = Column(String)
    url = Column(String)


class City(Base):
    __tablename__ = 'cities'

    id = Column(String, primary_key=True)
    name = Column(String)
    startField = Column(Integer, default=0)
    currentField = Column(Integer, default=0)
    taken = Column(Boolean, default=False)
    counter = Column(Integer, default=0)
